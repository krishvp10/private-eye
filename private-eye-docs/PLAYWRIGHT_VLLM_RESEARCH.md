# Playwright ARIA snapshots and vLLM Qwen2.5-VL serving

**Checked:** 2026-09-10  
**Scope:** Official Playwright documentation/source and official vLLM documentation/source only.  
**Repository convention:** Uppercase topic-specific Markdown notes under `private-eye-docs/`, with concise sections and inline source links.

## Executive findings

- The Playwright Python API exposes `Page.aria_snapshot()` and
  `Locator.aria_snapshot()`, returning a YAML representation of the accessibility
  tree. The Python options relevant to an agent are `mode="ai"` and `depth`
  (both added in v1.59), plus `boxes=True` (added in v1.60). [Python Page API,
  `page.aria_snapshot` section](https://playwright.dev/python/docs/api/class-page#page-aria-snapshot);
  [Python Locator API, `locator.aria_snapshot` section](https://playwright.dev/python/docs/api/class-locator#locator-aria-snapshot)
- AI mode changes the snapshot semantics, not only its formatting: it adds
  element references, does not wait for a locator match and throws if none
  matches, and includes snapshots for iframes inside the target. [Playwright
  Locator API source, AI-mode details, lines 209-218](https://github.com/microsoft/playwright/blob/main/docs/src/api/class-locator.md#L209-L218)
- YAML `boxes=True` appends `[box=x,y,width,height]`; coordinates are viewport-relative
  CSS pixels from `Element.getBoundingClientRect()`. [Python Locator API,
  `boxes` option](https://playwright.dev/python/docs/api/class-locator#locator-aria-snapshot-option-boxes)
- Playwright v1.63 adds `Locator.ariaSnapshotJSON` and `Page.ariaSnapshotJSON`,
  but the official API source marks these methods `langs: js`. The JSON form uses
  a `box` object with `x`, `y`, `width`, and `height` when boxes are enabled.
  [Playwright Locator API source, v1.63 JSON API and boxes, lines 242-295](https://github.com/microsoft/playwright/blob/main/docs/src/api/class-locator.md#L242-L295);
  [Playwright Page API source, v1.63 JSON API and boxes, lines 4426-4461](https://github.com/microsoft/playwright/blob/main/docs/src/api/class-page.md#L4426-L4461)
- The checked official Python API/source does not document or implement a
  `page.aria_snapshot_json()` / `locator.aria_snapshot_json()` method. The
  Python implementation exposes only `aria_snapshot(...)` with `mode`, `depth`,
  and `boxes`; treat the Python JSON spelling as unavailable unless the exact
  installed package proves otherwise. [Playwright Python `_page.py`, lines
  840-852](https://github.com/microsoft/playwright-python/blob/0e66a0927e5431b0f659ff41b6544de96b0486f5/playwright/_impl/_page.py#L840-L852);
  [Playwright Python `_locator.py`, current main commit, lines 589-604](https://github.com/microsoft/playwright-python/blob/0e66a0927e5431b0f659ff41b6544de96b0486f5/playwright/_impl/_locator.py#L589-L604)
- vLLM’s official Qwen2.5-VL recipe provides OpenAI-compatible `vllm serve`
  commands for Qwen2.5-VL-72B with TP=4 and Qwen2.5-VL-7B with DP=4. The
  current vLLM recipe landing page labels the Markdown guide a historical
  reference and directs users to `recipes.vllm.ai` for interactive, hardware-aware
  commands. [Official Qwen2.5-VL guide, current notice and GPU deployment sections](https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen2.5-VL.html#gpu-deployment);
  [official recipes landing page](https://recipes.vllm.ai/)
- vLLM’s OpenAI-compatible server supports `/v1/chat/completions`; its Chat API
  applies to text-generation models with a chat template, and the server
  documentation includes multimodal/vision-related support. [vLLM OpenAI-Compatible
  Server, “Supported APIs” and “Chat API” sections](https://docs.vllm.ai/en/stable/serving/online_serving/openai_compatible_server/#supported-apis)
- Structured outputs are enabled by default in the OpenAI-compatible server.
  Officially supported forms are `choice`, `regex`, `json`, `grammar`, and
  `structural_tag`; requests can use
  `extra_body={"structured_outputs": ...}`, while JSON Schema can use
  `response_format`. [vLLM Structured Outputs, “Online Serving (OpenAI API)”
  section](https://docs.vllm.ai/en/stable/features/structured_outputs/#online-serving-openai-api);
  [official source examples, lines 20-59](https://github.com/vllm-project/vllm/blob/main/docs/features/structured_outputs.md#L20-L59)

## Playwright Python 1.62/1.63 API status

### Python `aria_snapshot`

`page.aria_snapshot()` captures the page’s ARIA snapshot, and
`locator.aria_snapshot()` captures the snapshot for the matched element. The
Python reference describes the result as YAML markup whose nodes contain roles,
optional accessible names, state/value attributes, text, and child elements.
The page method was added in v1.59; the locator method was added in v1.49.
[`page.aria_snapshot` in the Python Page API](https://playwright.dev/python/docs/api/class-page#page-aria-snapshot);
[`locator.aria_snapshot` in the Python Locator API](https://playwright.dev/python/docs/api/class-locator#locator-aria-snapshot)

The Python options are:

| Option | Version | Behavior |
|---|---:|---|
| `mode="default"` or `"ai"` | v1.59 | `"ai"` returns a snapshot optimized for AI consumption. |
| `depth` | v1.59 | Limits snapshot depth when specified. |
| `boxes=True` | v1.60 | Appends each element’s box to the YAML snapshot. |

These version annotations and behaviors are in the official Python API
references. [`Locator.aria_snapshot` options](https://playwright.dev/python/docs/api/class-locator#locator-aria-snapshot);
[`Page.aria_snapshot` options](https://playwright.dev/python/docs/api/class-page#page-aria-snapshot)

### AI mode behavior

The official Locator API documents three AI-mode differences from the default
snapshot: element references such as `[ref=e2]` are included; Playwright does
not wait for the locator to match and throws when no element matches; and
snapshots of `<iframe>` elements inside the target are included. The Page API
documents the same reference/iframe behavior for page-level snapshots. [Locator
source docs, lines 209-218](https://github.com/microsoft/playwright/blob/main/docs/src/api/class-locator.md#L209-L218);
[Page source docs, lines 4398-4402](https://github.com/microsoft/playwright/blob/main/docs/src/api/class-page.md#L4398-L4402)

For this project, AI mode is therefore the appropriate Playwright Python
capture mode when the model needs stable element references, but the caller
must handle the documented no-match exception rather than relying on locator
auto-waiting.

### `boxes=True` behavior

In Python YAML snapshots, `boxes=True` appends
`[box=x,y,width,height]` to each element. The coordinates are relative to the
viewport, measured in CSS pixels, and come from
`Element.getBoundingClientRect()`. The default is `False`. [Python Locator API,
`boxes` option](https://playwright.dev/python/docs/api/class-locator#locator-aria-snapshot-option-boxes);
[Python Page API, `boxes` option](https://playwright.dev/python/docs/api/class-page#page-aria-snapshot-option-boxes)

This coordinate frame is suitable for correlating an ARIA node with a viewport
screenshot or for constructing a client-side redaction map, subject to the
normal effects of scrolling and page layout changes.

### What changes in Playwright v1.63

The official JavaScript release notes announce new
`Locator.ariaSnapshotJSON` and `Page.ariaSnapshotJSON` methods in v1.63. They
return the ARIA snapshot as a JSON value instead of YAML and accept `mode`,
`depth`, and `boxes` options. [Playwright JavaScript release notes, v1.63
“Locators” subsection](https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-js.md#L90-L93)

The API source is explicit that these methods are JavaScript-only
(`langs: js`) and that `boxes=True` adds a JSON `box` property with numeric
`x`, `y`, `width`, and `height` values in viewport-relative CSS pixels. [Locator
JSON API source, v1.63, lines 242-295](https://github.com/microsoft/playwright/blob/main/docs/src/api/class-locator.md#L242-L295);
[Page JSON API source, v1.63, lines 4426-4461](https://github.com/microsoft/playwright/blob/main/docs/src/api/class-page.md#L4426-L4461)

The current official Python release-note page has a Version 1.62 section; its
ARIA-snapshot release section is under Version 1.60, where the `boxes` feature
is recorded. The v1.63 JSON announcement is in the JavaScript release notes,
not the Python release notes. [Python release notes, Version 1.62 and Version
1.60 ARIA section](https://playwright.dev/python/docs/release-notes#version-162);
[JavaScript release notes, v1.63 locator announcement](https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-js.md#L90-L93)

### Python integration consequence

Use the Python API as follows:

```python
snapshot = page.aria_snapshot(mode="ai", depth=4, boxes=True)
```

That produces YAML, not the v1.63 JavaScript JSON shape. Do not write
`page.aria_snapshot_json()` or `locator.aria_snapshot_json()` against the
official Python API without first verifying a different installed package: the
checked Python implementation exposes `aria_snapshot(...)` only and sends the
`ariaSnapshot` channel with the Python options. [Playwright Python `_page.py`,
lines 840-852](https://github.com/microsoft/playwright-python/blob/0e66a0927e5431b0f659ff41b6544de96b0486f5/playwright/_impl/_page.py#L840-L852);
[Playwright Python `_locator.py`, current main commit, lines 589-604](https://github.com/microsoft/playwright-python/blob/0e66a0927e5431b0f659ff41b6544de96b0486f5/playwright/_impl/_locator.py#L589-L604)

## Current official vLLM Qwen2.5-VL serving

### Recipe status and installation

The official Qwen2.5-VL guide says it describes running the Qwen2.5-VL series
on the targeted accelerated stack and shows BF16 inference setup. Its current
notice says the Markdown guides are historical references and directs users to
the interactive `recipes.vllm.ai` site for up-to-date hardware selection and
copyable commands. [Official Qwen2.5-VL guide, current notice](https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen2.5-VL.html)

For NVIDIA, the official guide currently shows:

```bash
uv venv
source .venv/bin/activate
uv pip install -U vllm --torch-backend auto
```

For the documented AMD ROCm targets, it shows a separate wheel index and
requires Python 3.12, ROCm 7.0, and glibc >= 2.35 for that wheel. [Official
Qwen2.5-VL guide, “Installing vLLM”](https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen2.5-VL.html#installing-vllm)

### Qwen2.5-VL-72B, BF16, TP=4

The official 4xA100 example launches an OpenAI-compatible server on
`0.0.0.0:8000`, uses tensor parallelism across four GPUs, places the
multimodal encoder in data-parallel mode, and limits each prompt to two images
and zero videos:

```bash
export CUDA_VISIBLE_DEVICES=0,1,2,3
vllm serve Qwen/Qwen2.5-VL-72B-Instruct \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 4 \
  --mm-encoder-tp-mode data \
  --limit-mm-per-prompt '{"image":2,"video":0}'
```

[Official Qwen2.5-VL recipe source, lines 34-50](https://github.com/vllm-project/recipes/blob/main/Qwen/Qwen2.5-VL.md#L34-L50);
[rendered official guide, “Running Qwen2.5-VL-72B with BF16”](https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen2.5-VL.html#running-qwen25-vl-72b-with-bf16)

The same section notes that the default context length is 128K, suggests
`--max-model-len=65536` as a common memory-preserving setting, and explains
that the recipe’s `--mm-encoder-tp-mode data` is intended to avoid unnecessary
vision-encoder communication overhead. [Official Qwen2.5-VL guide, “Tips”
under the 72B section](https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen2.5-VL.html#tips)

### Qwen2.5-VL-7B-Instruct, DP=4

The official 4xA100 example uses data parallelism across four GPUs:

```bash
export CUDA_VISIBLE_DEVICES=0,1,2,3
vllm serve Qwen/Qwen2.5-VL-7B-Instruct \
  --host 0.0.0.0 \
  --port 8000 \
  --data-parallel-size 4 \
  --limit-mm-per-prompt '{"image":2,"video":0}'
```

[Official Qwen2.5-VL recipe source, lines 80-90](https://github.com/vllm-project/recipes/blob/main/Qwen/Qwen2.5-VL.md#L80-L90);
[rendered official guide, “Qwen2.5-VL-7B-Instruct with DP=4”](https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen2.5-VL.html#qwen25-vl-7b-instruct-with-dp4)

The guide says DP is generally preferable for medium-size models such as
Qwen2.5-VL-7B when throughput matters, while TP is generally more useful for
low-latency/low-load scenarios. This is a deployment recommendation from the
official recipe, not a universal hardware requirement. [Official Qwen2.5-VL
guide, parallelism explanation and 7B section](https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen2.5-VL.html#qwen25-vl-7b-instruct-with-dp4)

### OpenAI-compatible endpoint

vLLM documents an HTTP server implementing OpenAI Completions, Chat, and other
APIs. The supported API list includes Chat Completions at
`/v1/chat/completions`; Chat Completions apply to text-generation models with a
chat template. The same page documents multimodal/vision-related parameters
for chat requests. [vLLM OpenAI-Compatible Server, “Supported APIs” and “Chat
API”](https://docs.vllm.ai/en/stable/serving/online_serving/openai_compatible_server/#supported-apis)

For the repository’s client contract, the relevant base URL is therefore
normally `http://<host>:8000/v1`, with the model identifier matching the
served Qwen model. The official client examples use `base_url="http://localhost:8000/v1"`
and call `client.chat.completions.create(...)`. [vLLM OpenAI-Compatible Server,
Completions/Chat examples](https://docs.vllm.ai/en/stable/serving/online_serving/openai_compatible_server/#completions-api)

## vLLM structured outputs

### Supported forms and defaults

The official structured-output documentation says OpenAI-compatible Chat and
Completions APIs support:

- `choice`: output is exactly one of the choices;
- `regex`: output follows a regular expression;
- `json`: output follows a JSON Schema;
- `grammar`: output follows a context-free grammar; and
- `structural_tag`: JSON Schema-constrained content inside specified tags.

Structured outputs are enabled by default in the OpenAI-compatible server. The
server can select a backend automatically (`auto`) or receive an explicit
backend through `--structured-outputs-config.backend` on `vllm serve`. [vLLM
Structured Outputs, “Online Serving (OpenAI API)”](https://docs.vllm.ai/en/stable/features/structured_outputs/#online-serving-openai-api)

### Request forms

The official OpenAI-client example sends non-standard structured-output
parameters through `extra_body`:

```python
completion = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Classify this sentiment: vLLM is wonderful!"}],
    extra_body={"structured_outputs": {"choice": ["positive", "negative"]}},
)
```

The OpenAI-compatible server page shows the same `extra_body` pattern for
`structured_outputs`. [vLLM structured-output source, lines 20-40](https://github.com/vllm-project/vllm/blob/main/docs/features/structured_outputs.md#L20-L40);
[vLLM OpenAI-Compatible Server, “Extra Parameters”](https://docs.vllm.ai/en/stable/serving/online_serving/openai_compatible_server/#extra-parameters)

For JSON Schema, the official example uses OpenAI’s `response_format`:

```python
response_format={
    "type": "json_schema",
    "json_schema": {
        "name": "car-description",
        "schema": CarDescription.model_json_schema(),
    },
}
```

[vLLM structured-output source, JSON Schema example, lines 42-59](https://github.com/vllm-project/vllm/blob/main/docs/features/structured_outputs.md#L42-L59)

The current vLLM documentation also warns that deprecated `guided_json`,
`guided_regex`, `guided_choice`, and `guided_grammar` fields were removed in
v0.12.0 and should be replaced with the `structured_outputs` request shape.
[Official vLLM structured-output source, deprecation warning](https://github.com/vllm-project/vllm/blob/main/docs/features/structured_outputs.md#L1-L18)

## Project-specific implications

1. **Python client capture:** use `page.aria_snapshot(mode="ai", boxes=True,
   depth=...)` or the locator equivalent. Preserve the YAML output or parse it
   explicitly; do not assume the v1.63 JavaScript `ariaSnapshotJSON` method is
   available in Python. [Python Locator API](https://playwright.dev/python/docs/api/class-locator#locator-aria-snapshot);
   [Playwright v1.63 JavaScript JSON API](https://github.com/microsoft/playwright/blob/main/docs/src/api/class-locator.md#L242-L295)
2. **Grounding/redaction coordinates:** when `boxes=True`, treat coordinates as
   viewport CSS pixels and keep the screenshot and snapshot from the same page
   state so scrolling/layout changes do not invalidate the correlation. [Python
   Locator API, `boxes` option](https://playwright.dev/python/docs/api/class-locator#locator-aria-snapshot-option-boxes)
3. **Server launch:** the official Qwen recipe supports the repository’s
   Qwen2.5-VL path directly through `vllm serve`; choose the 7B DP=4 or 72B
   TP=4 example based on available hardware and throughput/latency goals.
   [Official Qwen2.5-VL guide](https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen2.5-VL.html#gpu-deployment)
4. **Structured action responses:** request the project’s JSON action schema
   using vLLM’s documented JSON-schema `response_format` or the
   `extra_body={"structured_outputs": {"json": ...}}` form, then retain
   independent client-side validation. Official vLLM docs establish API support,
   but the sources checked do not provide a Qwen2.5-VL-specific structured-output
   compatibility test; validate the exact vLLM/model build used in deployment.
   [vLLM Structured Outputs](https://docs.vllm.ai/en/stable/features/structured_outputs/#online-serving-openai-api)

## Source boundary and uncertainty

- This note intentionally excludes third-party blog posts, benchmark summaries,
  and community recipes.
- Playwright’s official sources clearly separate Python YAML
  `aria_snapshot` from JavaScript-only v1.63 `ariaSnapshotJSON`; the Python
  absence conclusion is limited to the official Python documentation and source
  checked above, not a claim about every unreleased or locally modified package.
- The official vLLM Qwen2.5-VL recipe documents serving commands and the
  structured-output documentation documents server/API support, but no checked
  official source proves that every Qwen2.5-VL checkpoint/build combination
  accepts every structured-output backend. Test the selected model, vLLM
  release, hardware, and request schema together.
