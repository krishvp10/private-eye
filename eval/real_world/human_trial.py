"""Human Baseline and Exploratory Usability Pilot Framework."""

from typing import Any

from pydantic import BaseModel, Field


class UsabilitySurveyResponse(BaseModel):
    user_id: str
    task_id: str
    accomplished_expected: bool
    knew_what_agent_was_doing: bool
    felt_comfortable_letting_continue: bool
    felt_needed_supervision: bool
    would_use_again_for_recurring: bool
    perceived_speed_rating: int = Field(ge=1, le=5)  # 1 (Very Slow) to 5 (Instant)
    perceived_trust_rating: int = Field(ge=1, le=5)  # 1 (No trust) to 5 (Complete trust)
    qualitative_feedback: str = ""


class HumanTrialComparator:
    """Compares Human Baseline vs PrivateEye Autonomous vs PrivateEye + Oversight."""

    @staticmethod
    def calculate_condition_comparison(
        human_results: list[dict[str, Any]],
        autonomous_results: list[dict[str, Any]],
        oversight_results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        # Filter strictly for mutually successful tasks to compute legitimate speedup
        matched_successes = []
        for h, a, o in zip(human_results, autonomous_results, oversight_results, strict=False):
            if h["success"] and a["success"]:
                speedup = round(h["duration_seconds"] / max(0.1, a["duration_seconds"]), 2)
                matched_successes.append({
                    "task_id": h["task_id"],
                    "human_seconds": h["duration_seconds"],
                    "agent_seconds": a["duration_seconds"],
                    "speedup": speedup,
                })

        mean_speedup = round(
            sum(m["speedup"] for m in matched_successes) / max(1, len(matched_successes)), 2
        ) if matched_successes else 0.0

        return {
            "mutually_successful_tasks_count": len(matched_successes),
            "mean_speedup_factor": mean_speedup,
            "matched_comparisons": matched_successes,
        }
