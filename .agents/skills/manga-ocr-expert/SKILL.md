---
name: manga-ocr-expert
description: Operational instructions, architectural doctrine, and quality verification gates for Japanese Manga OCR in Rust.
---

# Manga OCR Rust Expert Skill

This skill provides normative operational directives for maintaining, testing, and developing **Manga OCR Rust**.

---

## Operational Directives

1. **Pure Rust Invariant**: The repository is 100% Rust (`crates/` workspace). Do NOT re-introduce legacy Python files into the main runtime crates.
2. **Authority Hierarchy**:
   $$\text{Specification} \longrightarrow \text{Schemas/Contracts} \longrightarrow \text{Rust Substrate} \longrightarrow \text{PyO3/Adapters} \longrightarrow \text{Artifacts}$$
3. **Four-Tier Claim Taxonomy**: Always enforce strict claim taxonomy:
   $$\text{Documented} \neq \text{Implemented} \neq \text{Tested} \neq \text{Empirically Validated}$$

---

## Core Workspace Crates

- **`manga-ocr-core`**: Primitives, `OcrEngine` trait, Japanese `post_process()`, Furigana bracket FSM, multi-tile resampling, bubble reading order sorting.
- **`manga-ocr-pdp`**: `PanelEvaluator` struct, ACS consensus discounting, candidate selection.
- **`manga-ocr-ort`**: C++ ONNX Runtime bindings (`ort`), token entropy calculation ($H_k$), rolling loop truncation check.
- **`manga-ocr-cli`**: High-performance command-line binary (`manga-ocr`).
- **`manga-ocr-runtime`**: Titan-style Reflective Runtime microservice (Tokio + Axum).

---

## Verification Gates

Before declaring any work complete, execute:

```bash
cargo check --workspace
cargo test --workspace
python3 scripts/gen-llms.py
```
