"""
Unit tests for the PrivateEye Unified 1-Command Demo Supervisor (demo.py).
"""

import socket
import subprocess
import sys

import pytest

from demo import DemoSupervisor, PortConflictError, check_port_free, kill_process_tree


def test_check_port_free():
    # An ephemeral unbound port should be free
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    # Now it is closed
    assert check_port_free("127.0.0.1", port) is True


def test_port_conflict_detection():
    # Bind a real socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    s.listen(1)
    port = s.getsockname()[1]

    try:
        assert check_port_free("127.0.0.1", port) is False
        supervisor = DemoSupervisor(
            host="127.0.0.1",
            port_portal=port,
            open_browser=False,
        )
        with pytest.raises(PortConflictError):
            supervisor.check_ports()
    finally:
        s.close()


def test_supervisor_initialization():
    sup = DemoSupervisor(
        domain="patient",
        host="127.0.0.1",
        port_portal=9100,
        port_server=8100,
        port_dashboard=8180,
        open_browser=False,
    )
    assert sup.domain == "patient"
    assert sup.port_portal == 9100
    assert sup.port_server == 8100
    assert sup.port_dashboard == 8180
    assert sup.open_browser is False


def test_kill_process_tree_cleanly():
    # Spawn a sleeping dummy process
    cmd = [sys.executable, "-c", "import time; time.sleep(10)"]
    proc = subprocess.Popen(cmd)
    assert proc.poll() is None

    kill_process_tree(proc)
    # Process should be terminated
    assert proc.poll() is not None
