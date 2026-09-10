#!/usr/bin/env bash
set -euo pipefail

MODEL="${PRIVATEEYE_VLM_MODEL:-Qwen/Qwen2.5-VL-3B-Instruct}"
HOST="${VLLM_HOST:-0.0.0.0}"
PORT="${VLLM_PORT:-8000}"
MM_LIMIT="${VLLM_LIMIT_MM_PER_PROMPT:-{\"image\":2,\"video\":0}}"

exec vllm serve "$MODEL" \
  --host "$HOST" \
  --port "$PORT" \
  --limit-mm-per-prompt "$MM_LIMIT"
