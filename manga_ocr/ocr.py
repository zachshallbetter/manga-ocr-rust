from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Union

import jaconv
import torch
from loguru import logger
from PIL import Image
from transformers import AutoTokenizer, GenerationMixin, VisionEncoderDecoderModel, ViTImageProcessor


class MangaOcrModel(VisionEncoderDecoderModel, GenerationMixin):
    pass


class MangaOcr:
    def __init__(self, pretrained_model_name_or_path: str = "kha-white/manga-ocr-base", force_cpu: bool = False):
        logger.info(f"Loading OCR model from {pretrained_model_name_or_path}")
        self.processor = ViTImageProcessor.from_pretrained(pretrained_model_name_or_path)
        # explicit tokenizer_type works around transformers>=5.13 misdetecting the tokenizer class
        # for VisionEncoderDecoderModel configs and falling back to an incompatible fast-only backend
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path, tokenizer_type="bert-japanese")
        self.model = MangaOcrModel.from_pretrained(pretrained_model_name_or_path)

        if not force_cpu and torch.cuda.is_available():
            logger.info("Using CUDA")
            self.model.cuda()
        elif not force_cpu and torch.backends.mps.is_available():
            logger.info("Using MPS")
            self.model.to("mps")
        else:
            logger.info("Using CPU")

        example_path = Path(__file__).parent / "assets/example.jpg"
        if not example_path.is_file():
            raise FileNotFoundError(f"Missing example image {example_path}")
        self(example_path)

        logger.info("OCR ready")

    def __call__(
        self,
        img_or_path: str | Path | Image.Image,
        return_confidence: bool = False,
        return_dict: bool = False,
    ) -> str | dict[str, Any]:
        if isinstance(img_or_path, (str, Path)):
            img = Image.open(img_or_path)
        elif isinstance(img_or_path, Image.Image):
            img = img_or_path
        else:
            raise ValueError(f"img_or_path must be a path or PIL.Image, instead got: {img_or_path}")

        img = img.convert("L").convert("RGB")
        x = self._preprocess(img)

        if return_confidence or return_dict:
            gen_out = self.model.generate(
                x[None].to(self.model.device),
                max_length=300,
                return_dict_in_generate=True,
                output_scores=True,
            )
            seq = gen_out.sequences[0].cpu()
            text = self.tokenizer.decode(seq, skip_special_tokens=True)
            text = post_process(text)

            confidence = self._compute_confidence(gen_out.scores, seq)

            if return_dict:
                return {"text": text, "confidence": round(confidence, 4)}
            return text, round(confidence, 4)  # type: ignore

        x_out = self.model.generate(x[None].to(self.model.device), max_length=300)[0].cpu()
        text = self.tokenizer.decode(x_out, skip_special_tokens=True)
        text = post_process(text)
        return text

    def predict_batch(
        self,
        imgs_or_paths: list[str | Path | Image.Image],
        batch_size: int = 16,
        return_confidence: bool = False,
    ) -> list[str] | list[dict[str, Any]]:
        """
        Run OCR on a list of images in parallel matrix batches.

        :param imgs_or_paths: List of image paths or PIL Image objects.
        :param batch_size: Number of images to process per matrix batch.
        :param return_confidence: If True, returns dicts containing text and confidence score.
        """
        results = []
        for i in range(0, len(imgs_or_paths), batch_size):
            chunk = imgs_or_paths[i : i + batch_size]
            images = []
            for item in chunk:
                if isinstance(item, (str, Path)):
                    img = Image.open(item)
                elif isinstance(item, Image.Image):
                    img = item
                else:
                    raise ValueError(f"Item must be a path or PIL.Image, got: {item}")
                img = img.convert("L").convert("RGB")
                images.append(img)

            pixel_values = self.processor(images, return_tensors="pt").pixel_values.to(self.model.device)

            if return_confidence:
                gen_out = self.model.generate(
                    pixel_values,
                    max_length=300,
                    return_dict_in_generate=True,
                    output_scores=True,
                )
                seqs = gen_out.sequences.cpu()
                for b_idx, seq in enumerate(seqs):
                    text = self.tokenizer.decode(seq, skip_special_tokens=True)
                    text = post_process(text)
                    # Extract slice of scores for batch element b_idx
                    b_scores = [step_scores[b_idx : b_idx + 1] for step_scores in gen_out.scores]
                    conf = self._compute_confidence(b_scores, seq)
                    results.append({"text": text, "confidence": round(conf, 4)})
            else:
                out_seqs = self.model.generate(pixel_values, max_length=300).cpu()
                for seq in out_seqs:
                    text = self.tokenizer.decode(seq, skip_special_tokens=True)
                    text = post_process(text)
                    results.append(text)

        return results

    def _compute_confidence(self, scores: tuple[torch.Tensor, ...], sequence: torch.Tensor) -> float:
        if not scores:
            return 1.0

        token_probs = []
        # sequence[0] is start token, decoder outputs start from token index 1
        seq_tokens = sequence[1 : len(scores) + 1]

        for step_idx, step_scores in enumerate(scores):
            if step_idx >= len(seq_tokens):
                break
            probs = torch.softmax(step_scores[0], dim=-1)
            token_id = seq_tokens[step_idx].item()
            token_prob = probs[token_id].item()
            token_probs.append(token_prob)

        if not token_probs:
            return 1.0

        # Geometric mean of token probabilities
        log_sum = sum(torch.log(torch.tensor(max(p, 1e-6))).item() for p in token_probs)
        geom_mean = float(torch.exp(torch.tensor(log_sum / len(token_probs))).item())
        return min(max(geom_mean, 0.0), 1.0)

    def _preprocess(self, img: Image.Image) -> torch.Tensor:
        pixel_values = self.processor(img, return_tensors="pt").pixel_values
        return pixel_values.squeeze()


def post_process(text: str) -> str:
    text = "".join(text.split())
    text = text.replace("…", "...")
    text = re.sub("[・.]{2,}", lambda x: (x.end() - x.start()) * ".", text)
    text = jaconv.h2z(text, ascii=True, digit=True)

    return text
