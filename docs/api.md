# Manga OCR API Reference

This document provides a comprehensive reference for the public Python API and Command-Line Interface (CLI) of `manga-ocr`.

---

## Python API

### `manga_ocr.MangaOcr`

The primary inference class located in [`manga_ocr/ocr.py`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr/ocr.py#L14-L53).

#### Constructor

```python
MangaOcr(
    pretrained_model_name_or_path="kha-white/manga-ocr-base",
    force_cpu=False
)
```

##### Parameters
- `pretrained_model_name_or_path` (*str*, optional): Hugging Face Hub model ID or local directory path containing the model weights and tokenizer/processor config. Default: `"kha-white/manga-ocr-base"`.
- `force_cpu` (*bool*, optional): If `True`, forces model execution on CPU even if CUDA or Apple Silicon MPS acceleration is available. Default: `False`.

##### Initialization Logic
1. Loads [`ViTImageProcessor`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr/ocr.py#L17) for image feature extraction.
2. Loads [`AutoTokenizer`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr/ocr.py#L20) with explicit `tokenizer_type="bert-japanese"` (resolves compatibility issues with newer Hugging Face `transformers` versions).
3. Loads [`MangaOcrModel`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr/ocr.py#L11-L12) (inheriting from `VisionEncoderDecoderModel` and `GenerationMixin`).
4. Selects processing device (CUDA -> MPS -> CPU).
5. Performs a warmup inference using [`manga_ocr/assets/example.jpg`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr/assets/example.jpg) to compile execution graphs and verify readiness.

#### Invocation (`__call__`)

```python
__call__(img_or_path) -> str
```

##### Parameters
- `img_or_path` (*str* | *pathlib.Path* | *PIL.Image.Image*): Target image file path or pre-opened Pillow `Image` object.

##### Returns
- `str`: Recognized Japanese text normalized with post-processing rules.

##### Workflow
1. Opens image from path or validates PIL `Image` object.
2. Converts image to single channel grayscale (`L`), then converts to 3-channel `RGB`.
3. Pre-processes tensor via `ViTImageProcessor.pixel_values`.
4. Runs `model.generate()` with `max_length=300`.
5. Decodes token IDs with `tokenizer.decode(skip_special_tokens=True)`.
6. Passes raw decoded text through [`post_process()`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr/ocr.py#L60-L66).

---

### Text Post-Processing: `post_process(text)`

Located in [`manga_ocr/ocr.py`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr/ocr.py#L60-L66).

```python
def post_process(text: str) -> str
```

Applies the following transformation pipeline to raw token decoder strings:
1. Removes all whitespace (`"".join(text.split())`).
2. Normalizes full-width horizontal ellipses (`…` -> `...`).
3. Replaces repeated middle dots or periods (`[・.]{2,}`) with an equal count of standard periods (`.`).
4. Converts half-width ASCII characters and numbers to full-width equivalents via [`jaconv.h2z(text, ascii=True, digit=True)`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr/ocr.py#L64).

---

## Command-Line Interface (CLI)

The CLI tool is defined in [`manga_ocr/run.py`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr/run.py) and exposed as the `manga_ocr` entrypoint via `fire`.

### Usage Syntax

```bash
manga_ocr [READ_FROM] [WRITE_TO] [OPTIONS]
```

Or executed as a module:

```bash
python -m manga_ocr [READ_FROM] [WRITE_TO] [OPTIONS]
```

### Options Reference (`manga_ocr.run.run`)

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `read_from` | `str` | `"clipboard"` | Input source: `"clipboard"` to poll system clipboard images, or path to directory. |
| `write_to` | `str` | `"clipboard"` | Output destination: `"clipboard"` to copy recognized text to system clipboard, or path to a `.txt` file. |
| `pretrained_model_name_or_path` | `str` | `"kha-white/manga-ocr-base"` | Hugging Face model repository or local directory path. |
| `force_cpu` | `bool` | `False` | Forces CPU processing mode. |
| `delay_secs` | `float` | `0.1` | Polling loop delay interval in seconds when monitoring clipboard or directory. |
| `verbose` | `str/bool` | `False` | Unhides warning messages during image decoding errors. |

---

## CLI Operation Modes

### 1. Clipboard Polling Mode (Default)

```bash
manga_ocr
```
- Listens continuously for new image data on the system clipboard (`PIL.ImageGrab`).
- When a new image is detected (and differs from the previous sample verified via [`are_images_identical`](file:///Users/zachshallbetter/Projects/manga-ocr-rust/manga_ocr/run.py#L15-L22)), runs OCR and writes the resulting text back to the system clipboard using `pyperclip`.
- Linux desktop requirement: Requires `wl-clipboard` for Wayland sessions or `xclip` / `xsel` for X11 sessions.

### 2. Folder Watcher Mode

```bash
manga_ocr "/path/to/screenshots" --write_to="clipboard"
```
- Monitors the specified folder for newly added image files.
- Processes newly detected images, logs timing metrics via `loguru`, and outputs to clipboard or appends lines to a target text file.

### 3. File Logging Output Mode

```bash
manga_ocr "clipboard" "output.txt"
```
- Reads images from clipboard and appends recognized text to `output.txt` (UTF-8 encoding).
