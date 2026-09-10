# Qwen2.5-VL 3B/7B Serving via vLLM

**Checked:** 2026-09-10  
**Scope:** Official vLLM documentation/source, official Qwen model cards, and official GitHub Actions documentation only.

## Findings

- vLLM's supported-model registry maps `Qwen2_5_VLForConditionalGeneration` to Qwen2.5-VL and lists `Qwen/Qwen2.5-VL-3B-Instruct`; the same architecture covers the 7B checkpoint. [Supported models](https://github.com/vllm-project/vllm/blob/main/docs/models/supported_models.md) | [Registry](https://github.com/vllm-project/vllm/blob/main/vllm/model_executor/models/registry.py)
- vLLM exposes OpenAI-compatible Chat Completions at `/v1/chat/completions`; the documented client base URL is `http://localhost:8000/v1`. Multimodal chat uses OpenAI-style content parts, and `image_url.detail` is not supported. [Server docs](https://docs.vllm.ai/en/stable/serving/online_serving/openai_compatible_server/) | [Multimodal docs](https://docs.vllm.ai/en/stable/features/multimodal_inputs/#online-serving)
- Qwen's cards describe image/video inputs, a default visual-token range of 4-16,384 per image, and a 32,768-token published context. These are model-card limits, not a promise that every vLLM release preserves every behavior. [3B card](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct#image-resolution-for-performance-boost) | [7B card](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct#image-resolution-for-performance-boost)

## Installation and launch commands

The current Qwen recipe is marked a **historical reference** and directs users to [recipes.vllm.ai](https://recipes.vllm.ai/) for current hardware-aware commands. Its NVIDIA installation snippet is:

```bash
uv venv
source .venv/bin/activate
uv pip install -U vllm --torch-backend auto
```

[VERSION-DEPENDENT] The same page documents a separate ROCm wheel requiring Python 3.12, ROCm 7.0, and glibc >= 2.35. Do not reuse it for NVIDIA or assume other accelerators share its flags. [Recipe installation](https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen2.5-VL.html#installing-vllm)

### Qwen2.5-VL-3B-Instruct

The checked Qwen 3B card does **not** publish a vLLM-specific command. This is the least-assumption composition of vLLM's documented `vllm serve <model>` syntax and the official model identifier; it contains no hardware tuning:

```bash
vllm serve Qwen/Qwen2.5-VL-3B-Instruct \
  --host 0.0.0.0 \
  --port 8000
```

[VERSION-DEPENDENT] Validate it against the chosen vLLM release and accelerator. The support claim is from vLLM's model registry, not a 3B-specific recipe. [Server arguments](https://docs.vllm.ai/en/stable/configuration/serve_args/) | [Qwen 3B card](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct)

### Qwen2.5-VL-7B-Instruct

The official recipe publishes this exact BF16 example for **4x A100**:

```bash
export CUDA_VISIBLE_DEVICES=0,1,2,3
vllm serve Qwen/Qwen2.5-VL-7B-Instruct \
  --host 0.0.0.0 \
  --port 8000 \
  --data-parallel-size 4 \
  --limit-mm-per-prompt '{"image":2,"video":0}'
```

This is not a universal 7B recipe; no single-GPU command is asserted. [Official 7B recipe](https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen2.5-VL.html#qwen25-vl-7b-instruct-with-dp4)

## OpenAI-compatible multimodal request

The documented request shape uses text and `image_url` content parts. Replace the model with the identifier returned by `/v1/models`:

```python
from openai import OpenAI

client = OpenAI(base_url='http://localhost:8000/v1', api_key='-')
completion = client.chat.completions.create(
    model='Qwen/Qwen2.5-VL-3B-Instruct',
    messages=[{'role': 'user', 'content': [
        {'type': 'text', 'text': 'Describe this image in one sentence.'},
        {'type': 'image_url', 'image_url': {'url': 'https://example.com/image.jpg'}},
    ]}],
)
```

See [vLLM multimodal serving](https://docs.vllm.ai/en/stable/features/multimodal_inputs/#online-serving) and the [Qwen 3B input examples](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct#more-usage-tips).

## Multimodal limits

- `--limit-mm-per-prompt` is vLLM's per-prompt instance limit. The official recipe uses two images and zero videos; this is traffic control, not a model-intrinsic maximum. [Recipe tips](https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen2.5-VL.html#tips)
- Qwen's published visual-token range is 4-16,384 per image. `min_pixels`/`max_pixels` are supported, and explicit dimensions are rounded to a multiple of 28. [Qwen 3B resolution](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct#image-resolution-for-performance-boost) | [Qwen 7B resolution](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct#image-resolution-for-performance-boost)
- [VERSION-DEPENDENT] vLLM says multimodal support is actively iterating. Record image/video counts, pixel bounds, context length, and vLLM release together; do not infer hardware capacity from parameter count alone. [Multimodal guide](https://docs.vllm.ai/en/stable/features/multimodal_inputs/)

## Structured outputs

vLLM's OpenAI-compatible server supports structured outputs by default. Documented forms are `choice`, `regex`, `json`, `grammar`, and `structural_tag`; JSON Schema uses `response_format`:

```python
completion = client.chat.completions.create(
    model='Qwen/Qwen2.5-VL-3B-Instruct',
    messages=[{'role': 'user', 'content': 'Return the next action.'}],
    response_format={
        'type': 'json_schema',
        'json_schema': {
            'name': 'agent-action',
            'schema': {
                'type': 'object',
                'properties': {'action': {'type': 'string'}},
                'required': ['action'],
                'additionalProperties': False,
            },
        },
    },
)
```

The vLLM-specific alternative is `extra_body={'structured_outputs': {'json': schema}}`. [Structured outputs](https://docs.vllm.ai/en/stable/features/structured_outputs/) | [Extra parameters](https://docs.vllm.ai/en/stable/serving/online_serving/openai_compatible_server/#extra-parameters)

[VERSION-DEPENDENT] vLLM says `guided_json`, `guided_regex`, `guided_choice`, `guided_grammar`, and `guided_whitespace_pattern` were removed in v0.12.0. Use `structured_outputs` or `response_format` for current releases. The official sources do not prove every Qwen checkpoint/release/backend combination has been tested; keep independent response-schema validation.

## Health checks and endpoint security

- `GET /health` is the vLLM liveness/readiness check: the current source returns HTTP 200 after `client.check_health()` succeeds and HTTP 503 when the engine is dead. [Health-check source](https://github.com/vllm-project/vllm/blob/main/vllm/entrypoints/serve/instrumentator/health.py)
- `GET /v1/models` is the OpenAI-compatible model-discovery endpoint. Use it to obtain the served model identifier rather than assuming a local alias. [Models router](https://github.com/vllm-project/vllm/blob/main/vllm/entrypoints/openai/models/api_router.py)
- vLLM warns that `--api-key` protects `/v1`, `/v2`, and `/inference`, but not every endpoint, including `/health`; use network controls or a reverse proxy. [Authentication warning](https://docs.vllm.ai/en/stable/serving/online_serving/openai_compatible_server/)

Minimal checks:

```bash
curl -fsS http://localhost:8000/health
curl -fsS http://localhost:8000/v1/models
```

## CI validation boundary

The existing benchmark workflow is manually dispatched, defaults to a CI-safe `mock` mode, and runs the real endpoint path only when an operator supplies a configured endpoint. That is the correct boundary for GPU/model validation; normal PR CI should not invent hardware or silently download/run a VLM. [`benchmark.yml`](../.github/workflows/benchmark.yml)

GitHub's official workflow syntax requires YAML under `.github/workflows` and supports `workflow_dispatch` inputs, which the benchmark workflow uses. [Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)

## Caveats

- The checked sources do not publish a hardware-neutral, model-specific Qwen2.5-VL-3B vLLM recipe. The 3B command is deliberately un-tuned and must be validated on the selected release/runtime.
- The Qwen recipe page is version-sensitive and currently historical; prefer the interactive recipe for hardware-specific commands, then record the exact generated command and versions.
- Qwen cards and vLLM docs describe support independently. They do not establish a tested compatibility matrix for every vLLM, Transformers, accelerator, structured-output backend, image/video budget, or context-length combination.
