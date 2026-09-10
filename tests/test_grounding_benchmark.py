import json

from client.candidates import verify_ranked_candidates
from shared.protocol import SafeCandidate


def test_grounding_gate_rejects_ambiguous_candidates():
    candidates = [
        SafeCandidate(ref="e1", role="button", name="Continue", rank_score=0.60),
        SafeCandidate(ref="e2", role="button", name="Continue", rank_score=0.56),
    ]

    decision = verify_ranked_candidates(candidates)

    assert decision.selected_ref is None
    assert decision.ambiguous is True
    assert decision.reason == "ambiguous_margin"


def test_grounding_gate_accepts_clear_candidate():
    candidates = [
        SafeCandidate(ref="e1", role="button", name="Continue", rank_score=0.90),
        SafeCandidate(ref="e2", role="button", name="Cancel", rank_score=0.20),
    ]

    decision = verify_ranked_candidates(candidates)

    assert decision.selected_ref == "e1"
    assert decision.ambiguous is False


def test_150_case_benchmark_execution_and_privacy():
    from eval.grounding_benchmark import run_benchmark

    rep = run_benchmark()
    assert rep["total_cases"] == 150
    assert rep["metrics"]["target_accuracy"] > 0.80
    assert rep["metrics"]["candidate_recall_at_3"] > 0.95

    # Privacy verification: no raw vault secrets in benchmark output
    from client.vault import LocalVault

    vault = LocalVault()
    rep_text = json.dumps(rep)
    for secret in vault.get_all_raw_secrets():
        if len(secret) > 4:
            assert secret not in rep_text, f"Raw secret leaked into benchmark results: {secret}"
