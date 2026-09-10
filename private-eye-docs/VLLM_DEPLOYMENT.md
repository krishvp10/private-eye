# Qwen2.5-VL Deployment Harness

This is an explicit real-model path. It never changes `PRIVATEEYE_VLM_MODE` to
mock and does not claim a run succeeded when the endpoint is unavailable.

## GPU host

Use a Linux GPU host with a CUDA-compatible PyTorch/vLLM installation. The
repository requires the tested release to be supplied explicitly through
`VLLM_VERSION`; it does not invent a release pin:

```bash
export VLLM_VERSION=<tested-vllm-release>
bash scripts/install_vllm.sh
```

The model is selected without code changes:

```bash
export PRIVATEEYE_VLM_MODEL=Qwen/Qwen2.5-VL-3B-Instruct
bash scripts/start_vllm.sh
```

Repeat the exact benchmark with:

```bash
export PRIVATEEYE_VLM_MODEL=Qwen/Qwen2.5-VL-7B-Instruct
bash scripts/start_vllm.sh
```

The startup script also applies the official image-first safety limit
`{"image":2,"video":0}`. Override `VLLM_LIMIT_MM_PER_PROMPT` only when the
experiment explicitly requires another tested multimodal budget. Hardware-specific
tuning belongs on the GPU host and must be recorded with the experiment results
rather than guessed here.

## Health check

```bash
python scripts/check_vlm.py \
  --base-url http://GPU_HOST:8000/v1 \
  --model Qwen/Qwen2.5-VL-3B-Instruct
```

The endpoint must expose `/v1/models` and `/v1/chat/completions`.

## PrivateEye configuration

```bash
export PRIVATEEYE_VLM_MODE=real
export PRIVATEEYE_VLM_BASE_URL=http://GPU_HOST:8000/v1
export PRIVATEEYE_VLM_MODEL=Qwen/Qwen2.5-VL-3B-Instruct
export PRIVATEEYE_VLM_API_KEY=
python -m uvicorn server.api:app --host 0.0.0.0 --port 8100
```

## Experiments

```bash
python -m eval.real_vlm_experiment --server-url http://127.0.0.1:8100 --runs 5
python -m eval.context_ablation --server-url http://127.0.0.1:8100
```

Structured output is requested by the existing adapter with the `AgentAction`
JSON schema. Current vLLM documentation supports structured output through
`response_format`/structured-output request options; the client still validates
every response independently. See
`private-eye-docs/PLAYWRIGHT_VLLM_RESEARCH.md` for official source links.

Record the exact vLLM version, Transformers version, model identifier, GPU,
VRAM, CUDA/runtime, image dimensions, context variant, and latency metrics in
the generated report. Do not place prompts, screenshots, secrets, or API keys
in artifacts.
