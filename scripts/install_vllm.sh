#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${VLLM_VERSION:-}" ]]; then
  echo "Set VLLM_VERSION to the tested vLLM release before installing." >&2
  exit 2
fi
python -m pip install --upgrade "vllm==${VLLM_VERSION}"
python -m pip install --upgrade "openai>=1.99,<2"
echo "Installed vLLM ${VLLM_VERSION}. Verify with: vllm --version"
