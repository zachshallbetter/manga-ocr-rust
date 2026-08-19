# Manga OCR Rust

High-performance, zero-cost, multi-crate Rust workspace for optical character recognition of Japanese manga.

---

## Workspace Crates

- **[`manga-ocr-core`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/crates/manga-ocr-core)**: Pure Rust domain primitives, tokenization, full-width text normalization, and `OcrEngine` trait definitions.
- **[`manga-ocr-pdp`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/crates/manga-ocr-pdp)**: Polymorphic Decision Protocol engine, multi-engine panel evaluation, ACS consensus discounting, and Brier calibration.
- **[`manga-ocr-ort`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/crates/manga-ocr-ort)**: C++ ONNX Runtime bindings (`ort`) managing tensor memory, image resizing, and greedy/beam search token decoding (<120MB RAM).
- **[`manga-ocr-cli`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/crates/manga-ocr-cli)**: Fast, native command-line binary (`manga-ocr`).
- **[`manga-ocr-server`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/crates/manga-ocr-server)**: High-throughput Tokio/Axum REST and gRPC microservice.

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
cargo run --release -p manga-ocr-cli -- --image assets/examples/00.jpg
```

### Run Tokio/Axum Microservice

```bash
cargo run --release -p manga-ocr-server
```

---

## Documentation

Full architectural specifications, research doctrines, and API contracts are available in [`docs/`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs):

- [**Master Architecture & Systems Specification**](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/MASTER_ARCHITECTURE_SPECIFICATION.md)
- [**Architecture & Doctrine Synthesis**](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/architecture_and_doctrine.md)
- [**Reflective Rust Integration & Gains**](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/reflective_rust_integration.md)
- [**PDP Integration & Gains**](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/pdp_integration.md)
- [**IEPE Governance Integration & Gains**](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/iepe_integration.md)
- [**Theoretical & Conceptual Solutions**](file:///Users/zachshallbetter/Projects/manga-ocr-rust/docs/conceptual_gaps_and_solutions.md)
