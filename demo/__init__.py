"""PrivateEye Demonstration Suite Package.

Exposes demo scenario infrastructure while maintaining backward compatibility with root demo.py.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

# Maintain compatibility with root demo.py imports
_root_demo_path = Path(__file__).resolve().parent.parent / "demo.py"
if _root_demo_path.exists():
    _spec = importlib.util.spec_from_file_location("_root_demo_module", str(_root_demo_path))
    if _spec and _spec.loader:
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        for _name in [
            "DemoSupervisor",
            "PortConflictError",
            "check_port_free",
            "kill_process_tree",
        ]:
            if hasattr(_mod, _name):
                globals()[_name] = getattr(_mod, _name)
