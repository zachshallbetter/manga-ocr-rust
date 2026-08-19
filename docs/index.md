# Manga OCR Documentation Index

Welcome to the technical documentation for **Manga OCR** (`manga-ocr`). This repository contains the complete Python codebase for Manga OCR, an end-to-end optical character recognition system optimized for Japanese manga, as well as its synthetic data generation pipeline and model training scripts.

> [!NOTE]
> Although the working folder is named `manga-ocr-rust`, the project is written entirely in Python utilizing PyTorch, Hugging Face Transformers, OpenCV, Albumentations, and standard image processing libraries.

---

## Architecture & System Overview

Manga OCR is designed to recognize multi-line Japanese text formatted vertically or horizontally directly from image crops (such as speech bubbles or panel text) in a single forward pass without requiring line-by-line bounding box segmentation.

It utilizes the Hugging Face **Vision Encoder-Decoder** framework ([`VisionEncoderDecoderModel`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr/ocr.py#L11-L12)):
- **Vision Encoder**: Converts input image pixels into high-level visual representation feature vectors.
- **Text Decoder**: Auto-regressively predicts Japanese character tokens conditioned on the encoder output.

```mermaid
flowchart LR
    A[Input Image / Path] --> B[PIL Image Load & Grayscale Conversion]
    B --> C[ViTImageProcessor / Feature Extractor]
    C --> D[VisionEncoderDecoderModel]
    D --> E[Japanese BERT Tokenizer Decoding]
    E --> F[Japanese Text Post-Processing]
    F --> G[Recognized Text Output / Clipboard]
```

---

## Key Features

- **Multi-line Recognition**: Reads entire manga speech bubbles at once.
- **Complex Typesetting Support**: Handles vertical text (`writing-mode: vertical-rl`), furigana reading annotations, and *tate-chū-yoko* (horizontal numbers/ASCII in vertical text).
- **Flexible Deployment**: Supports CUDA, Apple Silicon MPS acceleration, and CPU fallback.
- **Daemon Background Processing**: Scans system clipboard or target directories continuously for screenshots (e.g. from ShareX, Flameshot, or macOS screenshot tools) and outputs recognized text to the clipboard or a log file.
- **Synthetic Data Generation Engine**: Employs headless Chromium (`html2image`) to render realistic synthetic Japanese manga text snippets with font styles, speech bubbles, and background art.

---

## Repository Documentation Map

- [**API & Microservice Reference**](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/api.md): Detailed reference for `MangaOcr`, batch inference API, ONNX engine, FastAPI REST server, Docker containerization, and CLI daemon parameters.
- [**Architecture & Doctrine Synthesis**](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/architecture_and_doctrine.md): Unifies Reflective Rust (RRSA), Polymorphic Decision Protocol (PDP), IEPE intent-evidence loops, Draft Smarter scoring/probabilities, and Titan production Rust runtime blueprints.
- [**Reflective Rust Integration & Gains**](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/reflective_rust_integration.md): Deep dive into RRSA integration, zero-overhead PyO3 FFI, compile-time tensor shape checks, and CSG model self-description.
- [**PDP Integration & Gains**](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/pdp_integration.md): Details Polymorphic Decision Protocol integration, ACS consensus discounting, Brier calibration, and invalidation triggers.
- [**IEPE Governance Integration & Gains**](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/iepe_integration.md): Details Intent and Evidence Project Engine qualification trace, ticket-first discipline, and verification gates.
- [**Agent, Skill & Automation Methods**](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/agent_and_skill_methods.md): Details agent orchestration, `.agents/skills` taxonomy, and `scripts/gen-llms.py` context compilation.
- [**Project Structure & Modules**](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/structure.md): Detailed layout of package boundaries, development modules, asset organization, and CI workflows.
- [**Synthetic Data Generator**](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/synthetic_data.md): Architecture of the Chromium-based synthetic data renderer, furigana typesetting engine, and augmentation pipeline.
- [**Model Training & Evaluation**](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/training.md): Detailed walkthrough of the training pipeline, dataset mixture composition, metrics calculation, and hyperparameter configuration.
- [**Page Processing Strategy**](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/page_processing_strategy.md): Architecture map and strategies for full-page OCR, color cover handling, and cross-panel text bubbles.
- [**Code Review & Audit Report**](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/code_review.md): Deep-dive audit report highlighting architectural strengths, known gaps, code smells, test coverage gaps, and a prioritized refactoring roadmap.

---

## Technology Stack

- **Python**: 3.9+
- **Deep Learning Framework**: [PyTorch](https://pytorch.org/), [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)
- **Computer Vision & Augmentation**: [OpenCV](https://opencv.org/), [Pillow](https://python-pillow.org/), [Albumentations](https://albumentations.ai/)
- **Japanese Text Processing**: `fugashi`, `unidic_lite`, `jaconv`, `budou` (TinySegmenter)
- **CLI & Monitoring**: `fire`, `loguru`, `pyperclip`, `wandb`
- **Synthetic Rendering**: `html2image` (Headless Chromium), `fontTools`
