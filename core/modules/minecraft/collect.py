import json
import os
import socket
import struct
import time
from typing import Optional

import psutil

from core.logger import log

DEFAULT_MINECRAFT_PORT = 25565
MAX_PROBE_TIMEOUT = 1.5
DETECTION_CACHE_TTL = 5.0

_DETECTION_CACHE = {
    "expires_at": 0.0,
    "servers": None,
}


def _write_varint(value: int) -> bytes:
    out = bytearray()
    while True:
        temp = value & 0x7F
        value >>= 7
        if value:
            temp |= 0x80
        out.append(temp)
        if not value:
            return bytes(out)


def _read_varint(sock: socket.socket) -> int:
    number = 0
    for index in range(5):
        chunk = sock.recv(1)
        if not chunk:
            raise ConnectionError("unexpected EOF while reading varint")
        value = chunk[0]
        number |= (value & 0x7F) << (7 * index)
        if not value & 0x80:
            return number
    raise ValueError("varint too long")


def _read_varint_from_bytes(data: bytes):
    number = 0
    for index, value in enumerate(data[:5]):
        number |= (value & 0x7F) << (7 * index)
        if not value & 0x80:
            return number, index + 1
    raise ValueError("varint too long")


def _write_string(value: str) -> bytes:
    encoded = value.encode("utf-8")
    return _write_varint(len(encoded)) + encoded


def _recv_exact(sock: socket.socket, size: int) -> bytes:
    chunks = bytearray()
    while len(chunks) < size:
        chunk = sock.recv(size - len(chunks))
        if not chunk:
            raise ConnectionError("unexpected EOF while reading packet")
        chunks.extend(chunk)
    return bytes(chunks)


def _extract_motd(description):
    if isinstance(description, str):
        return description
    if isinstance(description, dict):
        parts = [description.get("text", "")]
        for item in description.get("extra", []) or []:
            if isinstance(item, dict):
                parts.append(item.get("text", ""))
            elif isinstance(item, str):
                parts.append(item)
        return "".join(parts).strip()
    return None


def _extract_players(sample):
    if not isinstance(sample, list):
        return []
    return [item["name"] for item in sample if isinstance(item, dict) and item.get("name")]


def _safe_process_iter():
    try:
        yield from psutil.process_iter(["pid", "name", "cmdline", "cwd", "create_time"])
    except Exception as exc:
        log(f"Module minecraft KO lecture processus : {exc}")
        return


def _normalize_cmdline(cmdline):
    if not isinstance(cmdline, list):
        return []
    return [str(item) for item in cmdline if item]


def _is_java_process(proc_info: dict) -> bool:
    name = str(proc_info.get("name") or "").lower()
    cmdline = " ".join(_normalize_cmdline(proc_info.get("cmdline"))).lower()
    return "java" in name or " java" in f" {cmdline}"


def _looks_like_minecraft_server(proc_info: dict) -> bool:
    if not _is_java_process(proc_info):
        return False

    cmdline = " ".join(_normalize_cmdline(proc_info.get("cmdline"))).lower()
    indicators = (
        "server.jar",
        "minecraft_server",
        "paperclip",
        "paperspigot",
        "spigot",
        "purpur",
        "fabric-server-launch",
        "forge",
        "nogui",
    )
    return any(indicator in cmdline for indicator in indicators)


def _safe_net_connections(proc: psutil.Process):
    try:
        return proc.net_connections(kind="tcp")
    except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
        return []
    except Exception as exc:
        log(f"Module minecraft KO lecture connexions pid={proc.pid} : {exc}")
        return []


def _discover_port_from_connections(proc: psutil.Process):
    for conn in _safe_net_connections(proc):
        if conn.status != psutil.CONN_LISTEN or not conn.laddr:
            continue
        if conn.laddr.port:
            return int(conn.laddr.port)
    return None


def _discover_ports_from_connections(proc: psutil.Process):
    ports = []
    seen = set()

    for conn in _safe_net_connections(proc):
        if conn.status != psutil.CONN_LISTEN or not conn.laddr or not conn.laddr.port:
            continue

        port = int(conn.laddr.port)
        if port in seen:
            continue

        seen.add(port)
        ports.append(port)

    return ports


def _read_server_properties(path: str):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read().splitlines()
    except OSError:
        return []


def _discover_port_from_properties(proc_info: dict) -> Optional[int]:
    candidates = []

    cwd = proc_info.get("cwd")
    if cwd:
        candidates.append(os.path.join(cwd, "server.properties"))

    for arg in _normalize_cmdline(proc_info.get("cmdline")):
        lower = arg.lower()
        if lower.endswith(".jar"):
            parent = os.path.dirname(arg)
            if parent:
                candidates.append(os.path.join(parent, "server.properties"))

    seen = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)

        for line in _read_server_properties(candidate):
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() != "server-port":
                continue
            try:
                return int(value.strip())
            except ValueError:
                return None

    return None


def _build_detected_server(proc_info: dict) -> dict:
    pid = proc_info["pid"]
    process = psutil.Process(pid)

    port = _discover_port_from_connections(process)
    if port is None:
        port = _discover_port_from_properties(proc_info)
    if port is None:
        port = DEFAULT_MINECRAFT_PORT

    cwd = proc_info.get("cwd")
    name = f"minecraft-{pid}"
    if cwd:
        folder = cwd.replace("\\", "/").rstrip("/").rsplit("/", 1)[-1]
        if folder:
            name = folder

    return {
        "name": name,
        "kind": "java",
        "host": "127.0.0.1",
        "port": port,
        "pid": pid,
        "status": "running",
        "available": True,
        "reachable": False,
        "discovery": "local_process",
        "detected_via": "process",
        "started_at": int(proc_info.get("create_time") or time.time()),
        "cmdline": _normalize_cmdline(proc_info.get("cmdline")),
    }


def _build_detected_server_with_port(proc_info: dict, port: int, detected_via: str) -> dict:
    server = _build_detected_server(proc_info)
    server["port"] = int(port)
    server["detected_via"] = detected_via
    return server


def _probe_java_process_ports(proc_info: dict):
    pid = proc_info["pid"]

    try:
        process = psutil.Process(pid)
    except (psutil.NoSuchProcess, psutil.ZombieProcess):
        return None

    for port in _discover_ports_from_connections(process):
        try:
            _probe_java_server("127.0.0.1", int(port), min(MAX_PROBE_TIMEOUT, 0.75))
            return _build_detected_server_with_port(proc_info, port, "process_probe")
        except Exception:
            continue

    return None


def _detect_local_servers():
    now = time.monotonic()
    if _DETECTION_CACHE["servers"] is not None and now < _DETECTION_CACHE["expires_at"]:
        return [dict(item) for item in _DETECTION_CACHE["servers"]]

    servers = []
    seen_pids = set()

    for proc in _safe_process_iter():
        info = proc.info
        if _looks_like_minecraft_server(info):
            try:
                server = _build_detected_server(info)
            except (psutil.NoSuchProcess, psutil.ZombieProcess):
                continue
            except Exception as exc:
                log(f"Module minecraft KO detection pid={info.get('pid')} : {exc}")
                continue

            servers.append(server)
            seen_pids.add(info.get("pid"))
            continue

        if not _is_java_process(info):
            continue

        if info.get("pid") in seen_pids:
            continue

        try:
            server = _probe_java_process_ports(info)
            if server:
                servers.append(server)
                seen_pids.add(info.get("pid"))
        except Exception as exc:
            log(f"Module minecraft KO detection probe pid={info.get('pid')} : {exc}")

    _DETECTION_CACHE["servers"] = [dict(item) for item in servers]
    _DETECTION_CACHE["expires_at"] = now + DETECTION_CACHE_TTL
    return servers


def _probe_java_server(host: str, port: int, timeout: float):
    started_at = time.perf_counter()
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.settimeout(timeout)

        handshake = (
            _write_varint(0)
            + _write_varint(758)
            + _write_string(host)
            + struct.pack(">H", port)
            + _write_varint(1)
        )
        sock.sendall(_write_varint(len(handshake)) + handshake)
        sock.sendall(_write_varint(1) + _write_varint(0))

        packet_length = _read_varint(sock)
        packet = _recv_exact(sock, packet_length)
        packet_id, packet_id_size = _read_varint_from_bytes(packet)
        if packet_id != 0:
            raise ValueError("invalid status response packet")

        string_length, consumed = _read_varint_from_bytes(packet[packet_id_size:])
        payload_start = packet_id_size + consumed
        payload_end = payload_start + string_length
        payload = packet[payload_start:payload_end]
        status = json.loads(payload.decode("utf-8"))

        ping_payload = struct.pack(">q", int(time.time() * 1000))
        sock.sendall(_write_varint(9) + _write_varint(1) + ping_payload)
        _read_varint(sock)
        packet_id = _read_varint(sock)
        if packet_id != 1:
            raise ValueError("invalid ping response packet")
        _recv_exact(sock, 8)

        latency_ms = round((time.perf_counter() - started_at) * 1000, 2)

    players = status.get("players", {})
    return {
        "reachable": True,
        "latency_ms": latency_ms,
        "version": status.get("version", {}).get("name"),
        "protocol": status.get("version", {}).get("protocol"),
        "players_online": players.get("online"),
        "players_max": players.get("max"),
        "players_list": _extract_players(players.get("sample")),
        "motd": _extract_motd(status.get("description")),
    }


def _probe_detected_server(server: dict, timeout: float, failures: list):
    try:
        probe = _probe_java_server(server["host"], int(server["port"]), timeout)
        server.update(probe)
        server["probe_status"] = "ok"
    except Exception as exc:
        log(f"Module minecraft KO probe local pour {server['name']} : {exc}")
        failures.append(f"{server['name']}:{exc}")
        server["probe_status"] = "failed"
        server["probe_error"] = str(exc)


def _collect_configured_servers(module_config: dict, timeout: float, failures: list):
    servers = module_config.get("servers", [])
    results = []

    for index, server in enumerate(servers):
        host = server.get("host")
        port = int(server.get("port", DEFAULT_MINECRAFT_PORT))
        kind = (server.get("kind") or "java").lower()
        name = server.get("name") or f"minecraft-{index + 1}"

        if not host:
            failures.append(f"{name}:missing_host")
            results.append({
                "name": name,
                "kind": kind,
                "available": False,
                "status": "unknown",
                "error": "missing host",
            })
            continue

        item = {
            "name": name,
            "kind": kind,
            "host": host,
            "port": port,
            "available": False,
            "reachable": False,
            "status": "unknown",
            "discovery": "config",
        }

        try:
            if kind != "java":
                raise NotImplementedError(f"unsupported server kind: {kind}")

            item.update(_probe_java_server(host, port, timeout))
            item["available"] = True
            item["status"] = "running"
            item["probe_status"] = "ok"
        except Exception as exc:
            log(f"Module minecraft KO pour {name} : {exc}")
            failures.append(f"{name}:{exc}")
            item["probe_status"] = "failed"
            item["error"] = str(exc)

        results.append(item)

    return results


def collect_minecraft(module_config):
    timeout = min(float(module_config.get("timeout", MAX_PROBE_TIMEOUT)), MAX_PROBE_TIMEOUT)
    failures = []
    results = []

    detected_servers = _detect_local_servers()
    for server in detected_servers:
        _probe_detected_server(server, timeout, failures)
        results.append(server)

    if not results:
        results.extend(_collect_configured_servers(module_config, timeout, failures))

    return {
        "count": len(results),
        "available": sum(1 for item in results if item.get("available")),
        "servers": results,
        "partial_failures": failures,
        "timestamp": int(time.time()),
    }
