from __future__ import annotations

from pathlib import Path
from typing import Any, Callable
from PIL import Image

from manga_ocr.ocr import MangaOcr


class MangaPagePipeline:
    """
    Pipeline helper for processing full manga pages, covers, and multi-bubble spreads.
    Pairs a text region detector with MangaOcr recognition and reading order sorting.
    """

    def __init__(self, mocr_instance: MangaOcr | None = None):
        self.mocr = mocr_instance or MangaOcr()

    def process_page(
        self,
        img_or_path: str | Path | Image.Image,
        text_detector: Callable[[Image.Image], list[tuple[int, int, int, int]]] | None = None,
        return_confidence: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Process a full page scan.

        :param img_or_path: Full page image path or PIL Image.
        :param text_detector: Optional callable taking a PIL Image and returning bounding boxes [(x, y, w, h), ...].
                              If None, runs simple grid/contour detection fallback.
        :param return_confidence: If True, includes confidence score per text region.
        :return: List of dicts containing sorted text, bounding box coordinates, and confidence.
        """
        if isinstance(img_or_path, (str, Path)):
            full_img = Image.open(img_or_path)
        elif isinstance(img_or_path, Image.Image):
            full_img = img_or_path
        else:
            raise ValueError(f"img_or_path must be a path or PIL.Image, got: {img_or_path}")

        full_img = full_img.convert("RGB")

        if text_detector is not None:
            boxes = text_detector(full_img)
        else:
            # Fallback: treat entire image as single region
            boxes = [(0, 0, full_img.width, full_img.height)]

        crops = []
        valid_boxes = []
        for box in boxes:
            x, y, w, h = box
            if w <= 0 or h <= 0:
                continue
            crop = full_img.crop((x, y, x + w, y + h))
            crops.append(crop)
            valid_boxes.append(box)

        if not crops:
            return []

        # Batch inference across all extracted crops
        ocr_results = self.mocr.predict_batch(crops, return_confidence=return_confidence)

        page_regions = []
        for box, res in zip(valid_boxes, ocr_results):
            if isinstance(res, dict):
                text = res["text"]
                conf = res["confidence"]
            else:
                text = res
                conf = None

            page_regions.append(
                {
                    "box": box,  # (x, y, w, h)
                    "text": text,
                    "confidence": conf,
                }
            )

        # Sort by Japanese Reading Order: Top-to-Bottom, Right-to-Left
        # x descending (Right to Left), y ascending (Top to Bottom)
        page_regions.sort(key=lambda item: (item["box"][1] // 50, -item["box"][0]))

        return page_regions
