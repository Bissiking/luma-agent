import json
import socket
import struct
import time

from core.logger import log


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
        payload = packet[packet_id_size + consumed:packet_id_size + consumed + string_length]
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
        "available": True,
        "host": host,
        "port": port,
        "kind": "java",
        "latency_ms": latency_ms,
        "version": status.get("version", {}).get("name"),
        "protocol": status.get("version", {}).get("protocol"),
        "players_online": players.get("online"),
        "players_max": players.get("max"),
        "players_list": _extract_players(players.get("sample")),
        "motd": _extract_motd(status.get("description")),
    }


def collect_minecraft(module_config):
    timeout = float(module_config.get("timeout", 3.0))
    servers = module_config.get("servers", [])

    results = []
    failures = []

    for index, server in enumerate(servers):
        host = server.get("host")
        port = int(server.get("port", 25565))
        kind = (server.get("kind") or "java").lower()
        name = server.get("name") or f"minecraft-{index + 1}"

        if not host:
            failures.append(f"{name}:missing_host")
            results.append({
                "name": name,
                "kind": kind,
                "available": False,
                "error": "missing host",
            })
            continue

        try:
            if kind != "java":
                raise NotImplementedError(f"unsupported server kind: {kind}")

            probe = _probe_java_server(host, port, timeout)
            probe["name"] = name
            results.append(probe)
        except Exception as exc:
            log(f"Module minecraft KO pour {name} : {exc}")
            failures.append(f"{name}:{exc}")
            results.append({
                "name": name,
                "kind": kind,
                "host": host,
                "port": port,
                "available": False,
                "error": str(exc),
            })

    return {
        "count": len(results),
        "available": sum(1 for item in results if item.get("available")),
        "servers": results,
        "partial_failures": failures,
        "timestamp": int(time.time()),
    }
