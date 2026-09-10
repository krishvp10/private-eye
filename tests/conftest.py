"""
Shared pytest configuration for PrivateEye test suite.

Provides a thread-safe, race-free port allocation utility by keeping the
socket open until the server is ready to bind (SO_REUSEADDR approach).
"""
import socket


def allocate_port() -> int:
    """
    Allocate a free TCP port in a race-safe manner.

    Binds with SO_REUSEADDR so that uvicorn can re-use the port immediately
    even if the ephemeral socket is still in TIME_WAIT on some OS.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    return port
