"""Emergency Runtime Kill Switch for PrivateEye (Phase 9).

Provides a thread-safe, immediately effective kill switch that blocks any
subsequent model decisions, browser dispatches, or state mutations.
Generates structured immutable kill events conforming to OWASP ACS guidelines
for runtime human override and agent containment.
"""

from __future__ import annotations

import datetime
import threading
from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, List, Optional


@dataclass(frozen=True)
class KillSwitchEvent:
    event_id: str
    triggered_at_utc: str
    reason: str
    triggered_by: str
    interrupted_step: Optional[int]
    agent_state_before_stop: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class KillSwitchTriggeredError(RuntimeError):
    """Raised immediately when an action is attempted while kill switch is active."""
    def __init__(self, event: KillSwitchEvent):
        super().__init__(f"Agent halted by emergency kill switch: {event.reason}")
        self.event = event


class KillSwitch:
    """Thread-safe emergency stop mechanism for browser automation."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._engaged: bool = False
        self._event: Optional[KillSwitchEvent] = None
        self._listeners: List[Callable[[KillSwitchEvent], None]] = []

    @property
    def is_engaged(self) -> bool:
        with self._lock:
            return self._engaged

    def trigger(
        self,
        reason: str = "User initiated emergency halt",
        triggered_by: str = "user",
        interrupted_step: Optional[int] = None,
        agent_state: str = "executing",
    ) -> KillSwitchEvent:
        """Immediately engage the kill switch and notify listeners."""
        with self._lock:
            if not self._engaged:
                self._engaged = True
                event_id = f"kill_{int(datetime.datetime.now().timestamp() * 1000)}"
                now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
                self._event = KillSwitchEvent(
                    event_id=event_id,
                    triggered_at_utc=now_utc,
                    reason=reason,
                    triggered_by=triggered_by,
                    interrupted_step=interrupted_step,
                    agent_state_before_stop=agent_state,
                )
            event = self._event

        # Dispatch outside the lock to prevent deadlocks
        for listener in self._listeners:
            try:
                listener(event)
            except Exception:
                pass

        return event

    def reset(self) -> None:
        """Reset the kill switch (e.g. at the start of a fresh task)."""
        with self._lock:
            self._engaged = False
            self._event = None

    def add_listener(self, callback: Callable[[KillSwitchEvent], None]) -> None:
        """Register a callback invoked when kill switch fires."""
        self._listeners.append(callback)

    def assert_not_engaged(self) -> None:
        """Check guard and raise KillSwitchTriggeredError if engaged."""
        with self._lock:
            if self._engaged and self._event:
                raise KillSwitchTriggeredError(self._event)

    def get_event(self) -> Optional[KillSwitchEvent]:
        with self._lock:
            return self._event


# Global singleton instance for runtime and demo
GLOBAL_KILL_SWITCH = KillSwitch()
