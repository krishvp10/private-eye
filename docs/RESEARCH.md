# RESEARCH.md — Evidence Base

## Papers

| Paper | Authors | Year | Problem | Method | Results | Relevance | URL |
|---|---|---|---|---|---|---|---|
| GPT-4V(ision) is a Generalist Web Agent, if Grounded (SeeAct) | Zheng, Gou, Kil, Sun, Su (OSU) | ICML 2024 | LMM web agents | 2-stage: LMM plans text action → grounded to HTML element | 51.1% live-site success w/ oracle grounding; best non-oracle still 20–25 pts behind | **Core design evidence**: vision planning is strong, *grounding* is the bottleneck. Our client-side a11y tree + RedactionMap is the grounding layer, so the VLM never needs raw pixels for localization. | arxiv.org/abs/2401.01614 |
| Mind2Web | Deng et al. | NeurIPS 2023 | Generalist web agent dataset | 2,000+ tasks across 137 sites, action traces | SFT baselines modest; ICL generalizes better | Source of task shapes + evaluation splits for our benchmark. | openreview.net/forum?id=kiYqbO3wqw |
| WebArena | Zhou et al. | 2023 (ICLR 2024) | Realistic self-hosted web env | 812 tasks on sandboxed clones (Reddit/GitLab/e-commerce) | GPT-4 success ~14% | Defines realistic task success criteria; our demo sites mimic this pattern (self-hosted, resettable). | arxiv.org/abs/2307.13854 |
| OmniParser | Lu, Yang, Shen, Awadallah (Microsoft) | 2024 | Pure-vision screen parsing | YOLOv9-based icon detect + Florence-2 caption | Parses screenshots into interactable regions + semantics | icon_detect_v3 is MIT (usable); earlier Ultralytics-based weights are AGPL (flag). V1 candidate for on-device parsing. | arxiv.org/abs/2408.00203 |
| UI-TARS / UI-TARS-1.5 | Qin et al. (ByteDance) | Jan / Apr 2025 | Native GUI agent model | End-to-end VLM trained on GUI traces; system-2 reasoning | OSWorld 42.5 (1.5); ScreenSpot-Pro 61.6; WebVoyager 84.8 | Proof that 7B VLMs (Apache-2.0, trained from Qwen2.5-VL-7B) can drive GUI actions — our server's natural upgrade path. UI-TARS-2 (Sep 2025) is newer still. | arxiv.org/abs/2501.12326 |
| MIDV-500 | Arlazarov, Bulatov, Chernov | Computer Optics 2019 | ID-document video dataset | 500 clips × 50 doc types; per-frame doc/field/photo ground truth | Baselines: dlib face detect 87.5% (cropped docs) | Ground truth for our document/face redaction eval; all source docs public-domain/Wikimedia (license-clean). | arxiv.org/abs/1807.05786 |
| MIDV-2020 | Bulatov et al. | Computer Optics 2022 | Comprehensive ID benchmark | Extends MIDV family w/ generated photos | — | Alternative eval set; face images by generated.photos (synthetic — privacy-clean). | computeroptics.ru |
| WIDER FACE | Yang et al. | CVPR 2016 | Face detection benchmark | 32k images, 393k faces, 61 event classes | Standard AP benchmark | Recall target-setting for our face channel. License: free for research only — do not redistribute. | mmlab.ie.cuhk.edu.hk/projects/WIDERFace |
| Set-of-Mark Prompting | Yang et al. | 2023 | Visual grounding for LMMs | Overlay numbered markers on image | Big gains on referring tasks; *not* effective for web agents (SeeAct) | We deliberately avoid SoM overlays on outbound images (breaks redaction cleanliness); we ground via a11y tree instead. | arxiv.org/abs/2310.11441 |

## How research shapes the implementation

1. **SeeAct's grounding gap → our key architectural bet.** The 20–25 pt oracle gap exists because LMMs
   must map pixels to elements. We eliminate that entirely: the client sends an a11y tree (exact roles,
   names, states) + element bounding boxes. The VLM only *decides*, it doesn't *find*. This is our
   accuracy story for metric 1.
2. **SeeAct's online eval harness already uses Playwright** — independent validation of our
   choice of Playwright as the execution substrate.
3. **UI-TARS/OmniParser** show strong open-weights GUI perception exists at 7B scale, all compatible
   with our Apache/MIT licensing posture (with the OmniParser AGPL caveat below).
4. **MIDV-500/WIDER FACE** give us license-clean, ground-truthed eval data for the two hardest
   redaction channels (ID documents, faces).
5. **India-specific PII**: no standard public corpus exists for Aadhaar/PAN redaction in screenshots —
   we therefore generate a labeled synthetic corpus (300 screens across 6 form archetypes). This is an
   honest gap we close ourselves (see ASSUMPTIONS.md A-004).

## Existing implementations studied

- **SeeAct / WebOlympus** (OSU-NLP-Group): Playwright-based agent; teaches the plan→ground→act loop.
- **browser-use** (MIT, ~114k stars): DOM-extraction agent, LLM picks element index. Fast, but sends
  raw DOM/text to the LLM — *no privacy layer*. Confirms the market gap we fill.
- **OmniParser** (Microsoft): vision-only parsing; great perception, but output goes straight to the
  LLM unredacted.
- **UI-TARS-desktop / Agent TARS**: full desktop agents; heavyweight, no privacy story.

## Known technical limitations (honest)

- Regex/NER PII detection will miss non-standard formats (custom masked inputs, images of text) —
  mitigated by DOM heuristics + vision channel, but residual recall gap remains (tracked in RISKS).
- Redaction quality depends on detection boxes; Playwright bounding boxes are exact for DOM elements,
  but face boxes have inherent jitter (tracked).
- Qwen2.5-VL in vLLM has a documented version-triangle (vLLM ≥0.7.2 + transformers ≥4.49 + matching
  flash-attn) — pin all three in requirements (verified via Databricks + vLLM issue trackers, 2025).
