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

## Repository Map

| Section | Description | Key Modules |
| :--- | :--- | :--- |
| **[API Reference](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/api.md)** | Public Python API and CLI reference | [`manga_ocr.MangaOcr`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr/ocr.py#L14-L53), [`manga_ocr.run`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr/run.py#L47-L137) |
| **[Repository Structure](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/structure.md)** | File taxonomy, package layout, and dependencies | [`manga_ocr`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr), [`manga_ocr_dev`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr_dev) |
| **[Synthetic Data Generation](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/synthetic_data.md)** | Synthetic image rendering pipeline | [`SyntheticDataGenerator`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr_dev/synthetic_data_generator/generator.py#L15-L72), [`Renderer`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr_dev/synthetic_data_generator/renderer.py#L13-L25) |
| **[Training Pipeline](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/training.md)** | Model setup, dataset mixing, and training loop | [`MangaDataset`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr_dev/training/dataset.py#L12-L103), [`get_model`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr_dev/training/get_model.py#L29-L71) |
| **[Code Review & Analysis](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/code_review.md)** | Comprehensive audit, technical debt, and recommendations | Architectural strengths, bugs, edge cases |

---

## Technology Stack

- **Python**: 3.9+
- **Deep Learning Framework**: [PyTorch](https://pytorch.org/), [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)
- **Computer Vision & Augmentation**: [OpenCV](https://opencv.org/), [Pillow](https://python-pillow.org/), [Albumentations](https://albumentations.ai/)
- **Japanese Text Processing**: `fugashi`, `unidic_lite`, `jaconv`, `budou` (TinySegmenter)
- **CLI & Monitoring**: `fire`, `loguru`, `pyperclip`, `wandb`
- **Synthetic Rendering**: `html2image` (Headless Chromium), `fontTools`
