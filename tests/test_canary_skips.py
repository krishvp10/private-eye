import argparse
import asyncio
import json

from eval.real_vlm_canary import main_async


def test_real_canaries_skip_without_real_mode(monkeypatch, tmp_path):
    monkeypatch.setenv("PRIVATEEYE_VLM_MODE", "mock")
    output = tmp_path / "canaries.json"
    report = asyncio.run(
        main_async(
            argparse.Namespace(
                url="http://127.0.0.1:1/kyc",
                server_url="http://127.0.0.1:1",
                output=str(output),
            )
        )
    )
    assert report["status"] == "SKIPPED"
    assert all(item["status"] == "SKIPPED" for item in json.loads(output.read_text())["canaries"])
