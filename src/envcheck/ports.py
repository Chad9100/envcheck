from __future__ import annotations

import socket
from pathlib import Path

from .config import get_ports, load_config
from .result import FAIL, PASS, Result


def port_is_free(port: int, host: str = "127.0.0.1") -> bool:
    if not 0 < port < 65536:
        return False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
        except OSError:
            return False
    return True


def check_ports(root: Path) -> list[Result]:
    ports = get_ports(load_config(root))
    if not ports:
        return [Result("ports", PASS, "no ports configured, skipped")]
    out = []
    for p in ports:
        if port_is_free(p):
            out.append(Result(f"port {p}", PASS, "free"))
        else:
            out.append(Result(f"port {p}", FAIL, "in use or not bindable"))
    return out
