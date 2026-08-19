from __future__ import annotations

import base64
import io
from typing import Any

from PIL import Image

try:
    import uvicorn
    from fastapi import FastAPI, File, HTTPException, UploadFile
    from pydantic import BaseModel
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


if HAS_FASTAPI:
    app = FastAPI(
        title="Manga OCR Microservice",
        description="REST API service for optical character recognition of Japanese manga",
        version="0.1.16",
    )

    _mocr_instance = None

    def get_ocr_instance():
        global _mocr_instance
        if _mocr_instance is None:
            from manga_ocr.ocr import MangaOcr

            _mocr_instance = MangaOcr()
        return _mocr_instance

    class OCRBase64Request(BaseModel):
        image: str  # Base64 encoded image string
        return_confidence: bool = True

    class OCRResponse(BaseModel):
        text: str
        confidence: float | None = None

    class BatchOCRResponse(BaseModel):
        results: list[OCRResponse]

    @app.get("/health")
    def healthcheck() -> dict[str, Any]:
        return {"status": "ok", "service": "manga-ocr"}

    @app.post("/ocr", response_model=OCRResponse)
    async def run_ocr(
        file: UploadFile | None = File(default=None),  # noqa: B008
        payload: OCRBase64Request | None = None,
    ) -> dict[str, Any]:
        mocr = get_ocr_instance()

        if file is not None:
            contents = await file.read()
            img = Image.open(io.BytesIO(contents))
        elif payload is not None:
            try:
                _header, encoded = payload.image.split(",", 1) if "," in payload.image else ("", payload.image)
                contents = base64.b64decode(encoded)
                img = Image.open(io.BytesIO(contents))
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid base64 image data: {e}") from e
        else:
            raise HTTPException(status_code=400, detail="Must provide either image file upload or JSON payload.")

        text, confidence = mocr(img, return_confidence=True)  # type: ignore
        return {"text": text, "confidence": confidence}

    @app.post("/ocr/batch", response_model=BatchOCRResponse)
    async def run_ocr_batch(files: list[UploadFile] = File(...)) -> dict[str, Any]:  # noqa: B008
        mocr = get_ocr_instance()
        images = []

        for file in files:
            contents = await file.read()
            images.append(Image.open(io.BytesIO(contents)))

        batch_results = mocr.predict_batch(images, return_confidence=True)
        return {"results": batch_results}


def start_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    if not HAS_FASTAPI:
        raise ImportError(
            "FastAPI and Uvicorn are required to start the Manga OCR server. "
            "Install them via `pip install fastapi uvicorn`."
        )
    uvicorn.run("manga_ocr.server:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    start_server()
