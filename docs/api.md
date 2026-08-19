# Manga OCR API & Microservice Reference

This document provides a comprehensive reference for the public Python API, Batch Prediction API, ONNX Runtime Engine, FastAPI REST Microservice, and CLI of `manga-ocr`.

---

## Python Core API

### `manga_ocr.MangaOcr`

The primary inference class located in [`manga_ocr/ocr.py`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr/ocr.py#L18).

#### Constructor

```python
MangaOcr(
    pretrained_model_name_or_path="kha-white/manga-ocr-base",
    force_cpu=False
)
```

##### Parameters
- `pretrained_model_name_or_path` (*str*, optional): Hugging Face Hub model ID or local directory path. Default: `"kha-white/manga-ocr-base"`.
- `force_cpu` (*bool*, optional): Forces CPU execution even if CUDA or Apple Silicon MPS acceleration is available. Default: `False`.

#### Single Image Invocation (`__call__`)

```python
__call__(
    img_or_path: str | Path | Image.Image,
    return_confidence: bool = False,
    return_dict: bool = False
) -> str | tuple[str, float] | dict[str, Any]
```

##### Parameters
- `img_or_path`: Target image file path or PIL `Image` object.
- `return_confidence` (*bool*, optional): If `True`, returns `(text, confidence_score)`.
- `return_dict` (*bool*, optional): If `True`, returns `{"text": text, "confidence": score}`.

##### Returns
- `str` (default): Recognized Japanese text string.
- `dict`: Formatted dict when `return_dict=True`.

---

### Batch Inference API: `predict_batch`

```python
predict_batch(
    imgs_or_paths: list[str | Path | Image.Image],
    batch_size: int = 16,
    return_confidence: bool = False
) -> list[str] | list[dict[str, Any]]
```

Executes matrix batch inference across multiple image crops in parallel, optimizing GPU/MPS throughput.

---

### ONNX Runtime Engine: `manga_ocr.MangaOcrOnnx`

Located in [`manga_ocr/onnx_engine.py`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr/onnx_engine.py).

```python
from manga_ocr import MangaOcrOnnx, export_to_onnx

# 1. Export PyTorch model to ONNX weights
encoder_path, decoder_path = export_to_onnx(output_dir="models/onnx")

# 2. Run lightweight ONNX Runtime engine (<200MB RAM, fast CPU/MPS startup)
onnx_mocr = MangaOcrOnnx(encoder_path=encoder_path, decoder_path=decoder_path)
text = onnx_mocr("path/to/img.jpg")
```

---

### Page Processing Pipeline: `manga_ocr.MangaPagePipeline`

Located in [`manga_ocr/pipeline.py`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr/pipeline.py).

```python
from manga_ocr import MangaPagePipeline

pipeline = MangaPagePipeline()
# process_page accepts a custom bounding-box text detector
page_regions = pipeline.process_page("cover.jpg", text_detector=my_detector, return_confidence=True)
# Returns list of dicts: [{"box": (x,y,w,h), "text": "...", "confidence": 0.98}, ...]
```

---

## FastAPI REST Microservice (`manga_ocr.server`)

Exposes a production REST API server located in [`manga_ocr/server.py`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr/server.py).

### Endpoints

| Method | Endpoint | Payload | Response | Description |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health` | None | `{"status": "ok"}` | Microservice healthcheck. |
| `POST` | `/ocr` | Image upload (`file`) OR Base64 JSON payload | `{"text": "...", "confidence": 0.985}` | Single image OCR transcription. |
| `POST` | `/ocr/batch` | Multipart image files (`files`) | `{"results": [{"text": "...", "confidence": 0.98}]}` | Batched multi-image OCR transcription. |

### Launching Microservice Server

```bash
python -m manga_ocr.server --port=8000
```

### Docker Container Deployment

```bash
docker build -t manga-ocr:latest .
docker run -p 8000:8000 manga-ocr:latest
```

---

## Command-Line Interface (CLI)

```bash
manga_ocr [READ_FROM] [WRITE_TO] [OPTIONS]
```

Monitors clipboard (`read_from="clipboard"`) or target directories for newly created images. Uses native `watchdog` filesystem event observers for instant triggers.
