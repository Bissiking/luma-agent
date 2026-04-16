import ctypes
import platform
import time

import psutil

from core.alert_state import can_trigger_alert, clear_alert
from core.alerts import push_alert
from core.config import load_config
from core.installation import collect_installation_status
from core.logger import log
from core.services_collect import collect_services

psutil.cpu_percent(interval=None)


def inject_module(modules: dict, failures: list, name: str, fn):
    log(f"Tentative injection module : {name}")

    try:
        data = fn()
        if data is None:
            log(f"Module {name} n'a retourne aucune donnee")
            return

        if isinstance(data, dict) and data.get("partial_failures"):
            failures.extend(f"{name}:{item}" for item in data["partial_failures"])

        modules[name] = data
        log(f"Module {name} injecte avec succes")
    except Exception as e:
        failures.append(f"{name}:{e}")
        log(f"Module {name} indisponible : {e}")


def collect_network_core():
    import socket

    interfaces = []
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    for name, addr_list in addrs.items():
        stat = stats.get(name)
        if not stat or not stat.isup:
            continue

        ip = None
        for addr in addr_list:
            if addr.family == socket.AF_INET:
                ip = addr.address
                break

        if not ip:
            continue

        iface_type = (
            "loopback" if name.lower().startswith("lo")
            else "wifi" if name.lower().startswith(("wl", "wi"))
            else "ethernet"
        )

        interfaces.append({
            "name": name,
            "type": iface_type,
            "ip": ip,
        })

    io = psutil.net_io_counters(pernic=False)
    return {
        "interfaces": interfaces,
        "traffic": {
            "in": io.bytes_recv,
            "out": io.bytes_sent,
        },
    }


def _windows_volume_info(mountpoint):
    if platform.system() != "Windows":
        return {}

    root = mountpoint
    if len(root) >= 2 and root[1] == ":":
        root = f"{root[:2]}\\"

    drive_type_map = {
        2: "Disque amovible",
        3: "Disque local",
        4: "Partage reseau",
        5: "CD-ROM",
        6: "RAM Disk",
    }

    drive_type_id = ctypes.windll.kernel32.GetDriveTypeW(ctypes.c_wchar_p(root))
    drive_type = drive_type_map.get(drive_type_id, "Lecteur")

    vol_name = ctypes.create_unicode_buffer(261)
    fs_name = ctypes.create_unicode_buffer(261)
    serial = ctypes.c_uint(0)
    max_comp = ctypes.c_uint(0)
    flags = ctypes.c_uint(0)

    ok = ctypes.windll.kernel32.GetVolumeInformationW(
        ctypes.c_wchar_p(root),
        vol_name,
        len(vol_name),
        ctypes.byref(serial),
        ctypes.byref(max_comp),
        ctypes.byref(flags),
        fs_name,
        len(fs_name),
    )

    label = vol_name.value or None
    serial_hex = f"{serial.value:08X}" if ok else None
    filesystem = fs_name.value or None
    drive = root[:2] if len(root) >= 2 and root[1] == ":" else root.rstrip("\\")
    display_name = f"{label} ({drive})" if label else f"{drive_type} ({drive})"

    return {
        "label": label,
        "serial": serial_hex,
        "filesystem_windows": filesystem,
        "drive_type": drive_type,
        "display_name": display_name,
    }


def collect_metrics(include_modules=True):
    cfg = load_config()
    modules_cfg = cfg.get("modules", {})
    partial_failures = []

    hostname = platform.node()
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    uptime = int(time.time() - psutil.boot_time())
    network = collect_network_core()

    disks = []
    ghosted = cfg.get("ghosted_disks", [])

    for part in psutil.disk_partitions(all=False):
        if any(g.lower() in part.mountpoint.lower() for g in ghosted):
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            win_info = _windows_volume_info(part.mountpoint)
            disks.append({
                "device": part.device,
                "mount": part.mountpoint,
                "fstype": part.fstype,
                "total": round(usage.total / (1024 ** 3), 1),
                "used": round(usage.used / (1024 ** 3), 1),
                "free": round(usage.free / (1024 ** 3), 1),
                "percent": usage.percent,
                "label": win_info.get("label"),
                "serial": win_info.get("serial"),
                "filesystem_windows": win_info.get("filesystem_windows"),
                "drive_type": win_info.get("drive_type"),
                "display_name": win_info.get("display_name"),
            })
        except PermissionError:
            continue

    try:
        services = collect_services()
    except Exception as e:
        partial_failures.append(f"services:{e}")
        log(f"Erreur collecte services : {e}")
        services = {}

    core_metrics = {
        "hostname": hostname,
        "cpu": cpu,
        "ram": ram,
        "disks": disks,
        "uptime": uptime,
        "services": services,
        "network": network,
        "installation": collect_installation_status(),
    }

    module_metrics = {}

    if include_modules:
        if modules_cfg.get("docker"):
            log("Verification Docker...")
            from core.modules.docker.detect import docker_available

            if docker_available():
                from core.modules.docker.collect import collect_docker

                inject_module(module_metrics, partial_failures, "docker", collect_docker)
            else:
                log("Docker non disponible")

        minecraft_cfg = modules_cfg.get("minecraft", {})
        if isinstance(minecraft_cfg, dict) and minecraft_cfg.get("enabled"):
            from core.modules.minecraft.collect import collect_minecraft

            inject_module(
                module_metrics,
                partial_failures,
                "minecraft",
                lambda: collect_minecraft(minecraft_cfg),
            )

        if modules_cfg.get("gpu"):
            try:
                from core.modules.gpu.collect import collect_gpu

                inject_module(module_metrics, partial_failures, "gpu", collect_gpu)
            except Exception as e:
                partial_failures.append(f"gpu:{e}")
                log(f"Module gpu non charge : {e}")

        if modules_cfg.get("proxmox"):
            try:
                from core.modules.proxmox.collect import collect_proxmox

                inject_module(module_metrics, partial_failures, "proxmox", collect_proxmox)
            except Exception as e:
                partial_failures.append(f"proxmox:{e}")
                log(f"Module proxmox non charge : {e}")

    try:
        check_thresholds(cpu, ram, disks, cfg)
    except Exception as e:
        log(f"Erreur verification des seuils : {e}")

    return {
        "core": core_metrics,
        "modules": module_metrics,
        "partial_failures": partial_failures,
    }


def check_thresholds(cpu, ram, disks, cfg):
    cpu_th = cfg.get("cpu_threshold", 85)
    ram_th = cfg.get("ram_threshold", 85)
    disk_th = cfg.get("disk_threshold", 90)

    if cpu >= cpu_th:
        sev = "critical" if cpu >= cpu_th + 10 else "warning"
        if can_trigger_alert("cpu", sev):
            push_alert(sev, "cpu", f"CPU eleve ({cpu:.1f}%)", {"value": cpu})
    else:
        clear_alert("cpu")

    if ram >= ram_th:
        sev = "critical" if ram >= ram_th + 10 else "warning"
        if can_trigger_alert("ram", sev):
            push_alert(sev, "ram", f"RAM elevee ({ram:.1f}%)", {"value": ram})
    else:
        clear_alert("ram")

    for disk in disks:
        key = f"disk:{disk['mount']}"
        if disk["percent"] >= disk_th:
            sev = "critical" if disk["percent"] >= disk_th + 5 else "warning"
            if can_trigger_alert(key, sev):
                push_alert(
                    sev,
                    "disk",
                    f"Disque {disk['mount']} sature ({disk['percent']}%)",
                    {"mount": disk["mount"], "value": disk["percent"]},
                )
        else:
            clear_alert(key)
