from client.recovery import RecoveryController


def test_recovery_retries_non_destructive_failures_then_escalates():
    controller = RecoveryController(max_retries=2)
    first = controller.decide("grounding", 0, destructive=False)
    second = controller.decide("grounding", 1, destructive=False)
    third = controller.decide("grounding", 2, destructive=False)
    assert first.retry is True and first.retry_count == 1
    assert second.retry is True and second.retry_count == 2
    assert third.retry is False and third.escalate is True


def test_recovery_never_retries_destructive_or_policy_failures():
    controller = RecoveryController(max_retries=2)
    decision = controller.decide("policy", 0, destructive=True)
    assert decision.retry is False
    assert decision.escalate is True
