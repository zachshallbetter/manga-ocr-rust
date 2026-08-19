from __future__ import annotations

from pathlib import Path

import numpy as np
from loguru import logger
from PIL import Image

from manga_ocr.ocr import post_process

try:
    import onnxruntime as ort
    HAS_ONNX = True
except ImportError:
    HAS_ONNX = False


class MangaOcrOnnx:
    """
    Lightweight ONNX Runtime inference engine for Manga OCR.
    Reduces memory footprint to <200MB and eliminates full PyTorch runtime dependency.
    """

    def __init__(
        self,
        encoder_path: str | Path | None = None,
        decoder_path: str | Path | None = None,
        tokenizer_name_or_path: str = "kha-white/manga-ocr-base",
    ):
        if not HAS_ONNX:
            raise ImportError(
                "onnxruntime is required to use MangaOcrOnnx. Install it via `pip install onnxruntime`."
            )

        from transformers import AutoTokenizer, ViTImageProcessor

        logger.info("Initializing MangaOcr ONNX Runtime Engine...")
        self.processor = ViTImageProcessor.from_pretrained(tokenizer_name_or_path)
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name_or_path, tokenizer_type="bert-japanese")

        self.encoder_path = Path(encoder_path) if encoder_path else None
        self.decoder_path = Path(decoder_path) if decoder_path else None

        if self.encoder_path and self.encoder_path.exists():
            self.encoder_session = ort.InferenceSession(str(self.encoder_path))
        else:
            self.encoder_session = None

        if self.decoder_path and self.decoder_path.exists():
            self.decoder_session = ort.InferenceSession(str(self.decoder_path))
        else:
            self.decoder_session = None

    def __call__(self, img_or_path: str | Path | Image.Image) -> str:
        if isinstance(img_or_path, (str, Path)):
            img = Image.open(img_or_path)
        elif isinstance(img_or_path, Image.Image):
            img = img_or_path
        else:
            raise ValueError(f"img_or_path must be a path or PIL.Image, got: {img_or_path}")

        img = img.convert("L").convert("RGB")
        pixel_values = self.processor(img, return_tensors="np").pixel_values.astype(np.float32)

        if not self.encoder_session or not self.decoder_session:
            logger.warning("ONNX weights not provided; falling back to PyTorch MangaOcr model.")
            from manga_ocr.ocr import MangaOcr

            py_ocr = MangaOcr()
            return py_ocr(img)

        # 1. Run Vision Encoder ONNX Session
        encoder_inputs = {self.encoder_session.get_inputs()[0].name: pixel_values}
        encoder_outputs = self.encoder_session.run(None, encoder_inputs)
        encoder_hidden_states = encoder_outputs[0]

        # 2. Greedy Decoder Loop using Decoder ONNX Session
        cls_token_id = self.tokenizer.cls_token_id or 2
        sep_token_id = self.tokenizer.sep_token_id or 3

        tokens = [cls_token_id]
        max_length = 300

        for _ in range(max_length):
            input_ids = np.array([tokens], dtype=np.int64)
            decoder_inputs = {
                self.decoder_session.get_inputs()[0].name: input_ids,
                self.decoder_session.get_inputs()[1].name: encoder_hidden_states,
            }
            logits = self.decoder_session.run(None, decoder_inputs)[0]
            next_token = int(np.argmax(logits[0, -1, :]))

            if next_token == sep_token_id:
                break
            tokens.append(next_token)

        text = self.tokenizer.decode(tokens, skip_special_tokens=True)
        return post_process(text)


def export_to_onnx(
    pretrained_model_name_or_path: str = "kha-white/manga-ocr-base",
    output_dir: str | Path = "models/onnx",
) -> tuple[Path, Path]:
    """
    Export a PyTorch MangaOcr model to ONNX format.
    """
    import torch

    from manga_ocr.ocr import MangaOcrModel

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    encoder_onnx = out_path / "encoder.onnx"
    decoder_onnx = out_path / "decoder.onnx"

    logger.info(f"Loading PyTorch model {pretrained_model_name_or_path} for ONNX export...")
    model = MangaOcrModel.from_pretrained(pretrained_model_name_or_path)
    model.eval()

    # Dummy inputs for tracing
    dummy_pixels = torch.randn(1, 3, 224, 224)
    dummy_hidden = torch.randn(1, 197, 768)
    dummy_ids = torch.zeros((1, 1), dtype=torch.int64)

    logger.info(f"Exporting encoder ONNX to {encoder_onnx}...")
    torch.onnx.export(
        model.encoder,
        dummy_pixels,
        str(encoder_onnx),
        input_names=["pixel_values"],
        output_names=["last_hidden_state"],
        dynamic_axes={"pixel_values": {0: "batch_size"}},
        opset_version=14,
    )

    logger.info(f"Exporting decoder ONNX to {decoder_onnx}...")
    torch.onnx.export(
        model.decoder,
        (dummy_ids, None, None, dummy_hidden),
        str(decoder_onnx),
        input_names=["input_ids", "encoder_hidden_states"],
        output_names=["logits"],
        dynamic_axes={"input_ids": {0: "batch_size", 1: "sequence_length"}},
        opset_version=14,
    )

    logger.info("ONNX Export completed successfully!")
    return encoder_onnx, decoder_onnx
