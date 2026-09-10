# Phase 5: Real-VLM Evidence Plan

## Current gate

The repository is ready for live evidence, but the current workstation has no
reachable OpenAI-compatible Qwen endpoint. It does have an NVIDIA GeForce RTX
4060 Laptop GPU with 8188 MiB VRAM, but neither vLLM nor Ollama is installed
and the available WSL distribution is stopped. Therefore all live Qwen
measurements remain `SKIPPED` or `BLOCKED`.

## Required first milestone

Provision one serving runtime on a GPU host:

```text
GPU -> vLLM or Ollama -> Qwen2.5-VL-3B-Instruct
    -> OpenAI-compatible /v1 endpoint
    -> scripts/check_vlm.py
```

The endpoint must pass the health check and expose the configured model before
any result is counted.

## Experimental order

1. Image-only visual target canary.
2. Screenshot plus safe ScreenGraph grounding canary.
3. Sensitive fill using `value_ref` only.
4. Redaction non-reconstruction and prompt-injection canaries.
5. Destructive-action confirmation canary.
6. Full `/login -> /kyc -> /success` workflow.
7. Five consecutive workflows.
8. Context ablation: screenshot, screenshot plus graph, screenshot plus graph
   plus redaction metadata.
9. Identical Qwen2.5-VL-3B and Qwen2.5-VL-7B comparison.
10. Genuine packet and server-log inspection from those runs.

## Evidence rules

- `PASS` means the live endpoint returned a valid result and the local
  validator/executor verified it.
- `FAIL` means the live experiment ran and produced a measured failure.
- `SKIPPED` means the experiment could not run because the endpoint or required
  model was unavailable.
- Synthetic packet-audit results must never be presented as live Qwen privacy
  evidence.
- No workflow success, grounding accuracy, latency, or model ranking is
  reported until the corresponding live measurements exist.

## Commands on the GPU host

Set the endpoint explicitly:

```powershell
$env:PRIVATEEYE_VLM_MODE = "real"
$env:PRIVATEEYE_VLM_BASE_URL = "http://127.0.0.1:8000/v1"
$env:PRIVATEEYE_VLM_MODEL = "Qwen/Qwen2.5-VL-3B-Instruct"
```

Validate and run the staged experiments:

```powershell
python scripts/check_vlm.py --base-url "$env:PRIVATEEYE_VLM_BASE_URL" --model "$env:PRIVATEEYE_VLM_MODEL"
python -m eval.real_vlm_canary
python -m eval.real_vlm_experiment --runs 5
python -m eval.context_ablation --output eval/reports/context_ablation_real.json
python -m eval.model_comparison --output eval/reports/model_comparison_real.json
```

The Qwen 7B comparison must use the same browser states, prompts, schema,
decoding settings, and privacy configuration as the 3B run.
