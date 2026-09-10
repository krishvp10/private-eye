"""
PrivateEye Central Configuration Layer.
Reads infrastructure ports, hosts, and model endpoints from environment variables
with sane local defaults. Decouples runtime infrastructure from application logic.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    # Host and Networking
    HOST: str = os.getenv("PRIVATEEYE_HOST", "127.0.0.1")
    DEMO_HOST: str = os.getenv("PRIVATEEYE_DEMO_HOST", HOST)
    SERVER_HOST: str = os.getenv("PRIVATEEYE_SERVER_HOST", HOST)
    DASHBOARD_HOST: str = os.getenv("PRIVATEEYE_DASHBOARD_HOST", HOST)
    PORT_PORTAL: int = int(
        os.getenv("PRIVATEEYE_DEMO_PORT", os.getenv("PRIVATEEYE_PORT_PORTAL", "9001"))
    )
    PORT_SERVER: int = int(
        os.getenv("PRIVATEEYE_SERVER_PORT", os.getenv("PRIVATEEYE_PORT_SERVER", "8000"))
    )
    PORT_DASHBOARD: int = int(
        os.getenv(
            "PRIVATEEYE_DASHBOARD_PORT",
            os.getenv("PRIVATEEYE_PORT_DASHBOARD", "8080"),
        )
    )

    # VLM Backend Configuration
    VLM_MODE: str = os.getenv("PRIVATEEYE_VLM_MODE", "mock").lower()
    VLM_BASE_URL: str = os.getenv("PRIVATEEYE_VLM_BASE_URL", "http://127.0.0.1:11434/v1")
    VLM_MODEL: str = os.getenv("PRIVATEEYE_VLM_MODEL", "qwen2.5-vl:7b")

    @property
    def portal_url(self) -> str:
        return f"http://{self.DEMO_HOST}:{self.PORT_PORTAL}"

    @property
    def server_url(self) -> str:
        return f"http://{self.SERVER_HOST}:{self.PORT_SERVER}"

    @property
    def dashboard_url(self) -> str:
        return f"http://{self.DASHBOARD_HOST}:{self.PORT_DASHBOARD}"


# Global singleton instance
config = AppConfig()
