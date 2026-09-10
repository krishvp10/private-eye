"""
PrivateEye Unified 1-Command Demo Supervisor.

Single-entry point for evaluators and judges:
1. Validates port availability.
2. Supervises child services (Portal, API Server, Dashboard).
3. Polls HTTP health endpoints until fully ready.
4. Opens the interactive Visual Cockpit in the default browser.
5. Handles graceful Ctrl+C shutdown with process-tree cleanup (0 orphan processes).
"""

import argparse
import os
import signal
import socket
import subprocess
import sys
import time
import webbrowser

import httpx

from shared.config import config


class PortConflictError(Exception):
    """Raised when a required port is already bound by an existing process."""


class ServiceStartupError(Exception):
    """Raised when a managed service fails health checks within timeout."""


def check_port_free(host: str, port: int) -> bool:
    """Check if a network port is available for binding."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
        except OSError:
            return False
        return True


def kill_process_tree(proc: subprocess.Popen) -> None:
    """Terminate a process and all its child processes cleanly (Windows & POSIX safe)."""
    if proc.poll() is not None:
        return
    try:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        else:
            proc.terminate()
            proc.wait(timeout=2.0)
    except (OSError, subprocess.TimeoutExpired):
        try:
            proc.kill()
            proc.wait(timeout=2.0)
        except (OSError, subprocess.TimeoutExpired):
            return


class DemoSupervisor:
    """Supervises the lifecycle of PrivateEye demonstration services."""

    def __init__(
        self,
        domain: str = "kyc",
        host: str | None = None,
        port_portal: int | None = None,
        port_server: int | None = None,
        port_dashboard: int | None = None,
        open_browser: bool = True,
    ) -> None:
        self.domain = domain
        self.host = host or config.HOST
        self.port_portal = port_portal or config.PORT_PORTAL
        self.port_server = port_server or config.PORT_SERVER
        self.port_dashboard = port_dashboard or config.PORT_DASHBOARD
        self.open_browser = open_browser
        self.processes: dict[str, subprocess.Popen] = {}
        self._is_shutting_down = False

    def check_ports(self) -> None:
        """Verify that all required ports are free before spawning services."""
        ports = {
            "Portal": self.port_portal,
            "VLM Backend API": self.port_server,
            "Visual Dashboard": self.port_dashboard,
        }
        conflicts = []
        for name, p in ports.items():
            if not check_port_free(self.host, p):
                conflicts.append(f"  - {name} port {p} on {self.host} is already in use.")

        if conflicts:
            raise PortConflictError(
                "Cannot start PrivateEye Demo due to port conflicts:\n"
                + "\n".join(conflicts)
                + "\nPlease free the occupied ports or specify alternate ports via CLI arguments."
            )

    def start_service(
        self, name: str, module_name: str, env_vars: dict[str, str]
    ) -> subprocess.Popen:
        """Spawn a Python module as a supervised background subprocess."""
        env = dict(os.environ)
        env.update(env_vars)
        cmd = [sys.executable, "-m", module_name]
        proc = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.processes[name] = proc
        return proc

    def wait_for_health(self, timeout_seconds: float = 12.0) -> bool:
        """Poll health endpoints until all three services return 200 OK."""
        deadline = time.time() + timeout_seconds
        endpoints = [
            f"http://{self.host}:{self.port_portal}/login",
            f"http://{self.host}:{self.port_server}/v1/health",
            f"http://{self.host}:{self.port_dashboard}/api/state",
        ]

        with httpx.Client(timeout=1.0) as client:
            while time.time() < deadline:
                all_healthy = True
                for ep in endpoints:
                    try:
                        res = client.get(ep)
                        if res.status_code != 200:
                            all_healthy = False
                            break
                    except httpx.HTTPError:
                        all_healthy = False
                        break
                if all_healthy:
                    return True
                time.sleep(0.3)

        return False

    def launch(self) -> None:
        """Start all services, verify readiness, and display the cockpit banner."""
        print("\n" + "=" * 62)
        print("  PRIVATEEYE: PRIVACY-PRESERVING BROWSER AGENT SUPERVISOR")
        print("  Smart India Hackathon - Dept. of Space / ISRO (Problem 26171)")
        print("=" * 62 + "\n")

        print("[1/4] Checking network port availability...")
        self.check_ports()
        print(
            f"      OK Ports free: {self.port_portal} (Portal), "
            f"{self.port_server} (Backend), {self.port_dashboard} (Dashboard)"
        )

        print("[2/4] Spawning supervised services...")
        self.start_service(
            "portal",
            "demo_sites.server",
            {"PRIVATEEYE_PORT_PORTAL": str(self.port_portal), "PRIVATEEYE_HOST": self.host},
        )
        self.start_service(
            "server",
            "server.api",
            {"PRIVATEEYE_PORT_SERVER": str(self.port_server), "PRIVATEEYE_HOST": self.host},
        )
        self.start_service(
            "dashboard",
            "dashboard.app",
            {"PRIVATEEYE_PORT_DASHBOARD": str(self.port_dashboard), "PRIVATEEYE_HOST": self.host},
        )

        print("[3/4] Polling service health checks...")
        if not self.wait_for_health():
            self.shutdown()
            raise ServiceStartupError(
                "Services failed to become healthy within the timeout window."
            )

        dashboard_url = f"http://{self.host}:{self.port_dashboard}?domain={self.domain}"
        print("[4/4] All services healthy and verified!\n")

        banner = f"""+------------------------------------------------------------+
|  PrivateEye Live Cockpit Ready                             |
|------------------------------------------------------------|
|  - Visual Cockpit:   {dashboard_url:<37} |
|  - Portal Endpoint:  http://{self.host}:{self.port_portal:<29} |
|  - VLM Server API:   http://{self.host}:{self.port_server:<29} |
|  - Active Domain:    {self.domain.upper():<37} |
+------------------------------------------------------------+
|  Press Ctrl+C to terminate all services cleanly.           |
+------------------------------------------------------------+"""
        print(banner)

        if self.open_browser:
            print(f"\nOpening {dashboard_url} in your default browser...")
            webbrowser.open(dashboard_url)

    def shutdown(self) -> None:
        """Cleanly terminate all child processes and avoid orphans."""
        if self._is_shutting_down:
            return
        self._is_shutting_down = True
        print("\nInitiating graceful shutdown of all PrivateEye services...")
        for proc in self.processes.values():
            kill_process_tree(proc)
        print("OK All child processes stopped cleanly.\n")

    def run_until_interrupted(self) -> None:
        """Keep the supervisor alive until SIGINT (Ctrl+C) is received."""
        try:
            while True:
                # Check that child processes are still running
                for name, proc in self.processes.items():
                    if proc.poll() is not None:
                        print(
                            f"\nWarning: Service '{name}' exited unexpectedly with code {proc.poll()}."
                        )
                        self.shutdown()
                        return
                time.sleep(1.0)
        except KeyboardInterrupt:
            self.shutdown()


def main() -> None:
    parser = argparse.ArgumentParser(description="PrivateEye Unified 1-Command Demo Supervisor")
    parser.add_argument(
        "--domain",
        choices=["kyc", "checkout", "patient", "sample_fixture"],
        default="kyc",
        help="Domain to demonstrate",
    )
    parser.add_argument("--host", default=None, help="Host interface; defaults to PRIVATEEYE_HOST")
    parser.add_argument("--port-portal", type=int, default=None, help="Portal port")
    parser.add_argument("--port-server", type=int, default=None, help="VLM Server API port")
    parser.add_argument("--port-dashboard", type=int, default=None, help="Dashboard port")
    parser.add_argument(
        "--no-browser", action="store_true", help="Skip opening the default web browser"
    )
    args = parser.parse_args()

    supervisor = DemoSupervisor(
        domain=args.domain,
        host=args.host,
        port_portal=args.port_portal,
        port_server=args.port_server,
        port_dashboard=args.port_dashboard,
        open_browser=not args.no_browser,
    )

    # Setup signal traps
    def sig_handler(sig, frame):
        supervisor.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, sig_handler)

    try:
        supervisor.launch()
        supervisor.run_until_interrupted()
    except (PortConflictError, ServiceStartupError) as e:
        print(f"\nStartup Error: {e}", file=sys.stderr)
        supervisor.shutdown()
        sys.exit(1)


if __name__ == "__main__":
    main()
