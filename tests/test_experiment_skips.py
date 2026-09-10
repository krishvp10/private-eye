import json

from eval.model_comparison import main_async


def test_model_comparison_skips_without_real_mode(monkeypatch, tmp_path):
    monkeypatch.setenv("PRIVATEEYE_VLM_MODE", "mock")
    output = tmp_path / "model.json"
    import argparse
    import asyncio

    report = asyncio.run(
        main_async(
            argparse.Namespace(
                url="http://127.0.0.1:1/login",
                server_url="http://127.0.0.1:1",
                models=["Qwen/Qwen2.5-VL-3B-Instruct"],
                runs=1,
                max_steps=1,
                output=str(output),
            )
        )
    )
    assert report["status"] == "SKIPPED"
    assert json.loads(output.read_text())["models"][0]["status"] == "SKIPPED"
