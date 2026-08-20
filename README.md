# Manga OCR Rust

High-performance, zero-cost, multi-crate Rust workspace for optical character recognition of Japanese and English manga/comics.

---

## Workspace Crates & Packages

- **[`manga-ocr-core`](crates/manga-ocr-core)**: Pure Rust domain primitives, tokenization, multi-language post-processing (`Japanese`, `English`), Furigana FSM, multi-tile resampling, and `OcrEngine` trait definitions.
- **[`manga-ocr-pdp`](crates/manga-ocr-pdp)**: Polymorphic Decision Protocol engine, multi-engine panel evaluation, ACS consensus discounting, and Brier calibration.
- **[`manga-ocr-ort`](crates/manga-ocr-ort)**: C++ ONNX Runtime bindings (`ort`) managing tensor memory, image resizing, token entropy calculation ($H_k$), and loop truncation (<120MB RAM).
- **[`manga-ocr-cli`](crates/manga-ocr-cli)**: Fast, native command-line binary (`manga-ocr`).
- **[`manga-ocr-runtime`](crates/manga-ocr-runtime)**: High-throughput Tokio/Axum REST Reflective Runtime microservice.

---

## Quick Start

### Build Workspace

```bash
cargo build --release
```

### Run Tests

```bash
cargo test --workspace
```

### Run CLI

```bash
cargo run --release -p manga-ocr-cli -- --image assets/examples/00.jpg --extract-furigana
```

### Run Tokio/Axum Reflective Runtime

```bash
cargo run --release -p manga-ocr-runtime
```

---

## Documentation

Full architectural specifications, research doctrines, and API contracts:

- [**Master Architecture & Systems Specification**](docs/MASTER_ARCHITECTURE_SPECIFICATION.md)
- [**API & Schema Reference**](docs/api.md)
- [**Architecture & Doctrine Synthesis**](docs/architecture_and_doctrine.md)
- [**Reflective Rust Integration & Gains**](docs/reflective_rust_integration.md)
- [**PDP Integration & Gains**](docs/pdp_integration.md)
- [**IEPE Governance Integration & Gains**](docs/iepe_integration.md)
- [**Master TODO & Implementation Ledger**](docs/TODO.md)
