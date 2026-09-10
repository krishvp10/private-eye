"""Local privacy-safe candidate generation and deterministic ranking."""

import re
from collections.abc import Iterable
from dataclasses import dataclass
from difflib import SequenceMatcher

from shared.protocol import ActionType, SafeCandidate, ScreenGraph, ScreenNode

TOKEN_RE = re.compile(r"[a-z0-9]+")
INTERACTIVE_ROLES = {
    "button",
    "checkbox",
    "combobox",
    "link",
    "option",
    "radio",
    "select",
    "textbox",
    "input",
    "textarea",
}


@dataclass(frozen=True)
class GroundingDecision:
    """Local decision gate for ranked candidates."""

    selected_ref: str | None
    confidence: float
    ambiguous: bool
    reason: str


def _tokens(value: str) -> set[str]:
    return set(TOKEN_RE.findall(value.lower()))


def _role_for_action(action: ActionType | str | None) -> set[str]:
    value = action.value if isinstance(action, ActionType) else str(action or "")
    if value == ActionType.FILL.value:
        return {"textbox", "input", "textarea"}
    if value == ActionType.SELECT.value:
        return {"combobox", "select", "option"}
    if value == ActionType.CLICK.value:
        return INTERACTIVE_ROLES - {"textbox", "input", "textarea"}
    return INTERACTIVE_ROLES


def _walk(nodes: Iterable[ScreenNode]) -> Iterable[ScreenNode]:
    for node in nodes:
        yield node
        yield from _walk(node.children)


def generate_candidates(
    graph: ScreenGraph,
    task: str = "",
    action: ActionType | str | None = None,
    limit: int | None = None,
) -> list[SafeCandidate]:
    """Return only visible, locally executable, privacy-safe candidates."""
    task_tokens = _tokens(task)
    task_text = task.lower()
    for action_name in (item.value for item in ActionType):
        task_text = task_text.replace(action_name, " ")
    task_text = " ".join(task_text.split())
    allowed_roles = _role_for_action(action)
    candidates: list[SafeCandidate] = []
    for node in _walk(graph.root.children):
        if not node.ref or not node.visible or node.role.lower() not in allowed_roles:
            continue
        name_tokens = _tokens(node.name or "")
        lexical = (
            SequenceMatcher(None, task_text, (node.name or "").lower()).ratio()
            if task_tokens and name_tokens
            else 0.0
        )
        exact_bonus = 0.25 if task_text == (node.name or "").lower().strip() else 0.0
        role_bonus = 0.2 if node.role.lower() in allowed_roles else 0.0
        state_bonus = 0.1 if node.enabled else -0.3
        score = max(0.0, min(1.0, 0.7 * lexical + exact_bonus + role_bonus + state_bonus))
        safe_name = "[REDACTED FIELD]" if node.sensitive else (node.name or "")
        candidates.append(
            SafeCandidate(
                ref=node.ref,
                role=node.role,
                name=safe_name,
                sensitive=node.sensitive,
                visible=node.visible,
                enabled=node.enabled,
                bbox=node.bbox,
                rank_score=round(score, 4),
            )
        )
    candidates.sort(key=lambda item: (-item.rank_score, item.ref))
    return candidates[:limit] if limit else candidates


def verify_ranked_candidates(
    candidates: list[SafeCandidate],
    *,
    min_confidence: float = 0.45,
    min_margin: float = 0.10,
) -> GroundingDecision:
    """Reject low-confidence or ambiguous local rankings instead of guessing."""
    if not candidates:
        return GroundingDecision(None, 0.0, True, "no_candidates")
    top = candidates[0]
    second_score = candidates[1].rank_score if len(candidates) > 1 else 0.0
    margin = top.rank_score - second_score
    if not top.enabled:
        return GroundingDecision(None, top.rank_score, True, "top_candidate_disabled")
    if top.rank_score < min_confidence:
        return GroundingDecision(None, top.rank_score, True, "low_confidence")
    if len(candidates) > 1 and margin < min_margin:
        return GroundingDecision(None, top.rank_score, True, "ambiguous_margin")
    return GroundingDecision(top.ref, top.rank_score, False, "accepted")
