import json

from client.vault import LocalVault
from eval.leak_check import OutboundLeakInterceptor


def test_privacy_report_is_machine_readable_and_secret_free():
    interceptor = OutboundLeakInterceptor(LocalVault())
    report = interceptor.inspect_request(
        url="https://agent.example/v1/analyze",
        headers={"content-type": "application/json"},
        body=b'{"image_b64":"sanitized","value_ref":"user_profile.pan"}',
    )
    assert report["safe"] is True
    assert report["checked_components"] == ["url", "headers", "body"]
    assert "ABCDE1234F" not in json.dumps(report)
