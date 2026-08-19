from pathlib import Path
from PIL import Image

from manga_ocr import MangaOcr, MangaPagePipeline

TEST_DATA_ROOT = Path(__file__).parent / "data"


def test_confidence_score():
    mocr = MangaOcr()
    img_path = TEST_DATA_ROOT / "images" / "00.jpg"

    # Test dict return
    res_dict = mocr(img_path, return_dict=True)
    assert isinstance(res_dict, dict)
    assert "text" in res_dict
    assert "confidence" in res_dict
    assert isinstance(res_dict["confidence"], float)
    assert 0.0 <= res_dict["confidence"] <= 1.0
    assert res_dict["text"] == "素直にあやまるしか"

    # Test tuple return
    text, conf = mocr(img_path, return_confidence=True)
    assert text == "素直にあやまるしか"
    assert isinstance(conf, float)
    assert 0.0 <= conf <= 1.0


def test_predict_batch():
    mocr = MangaOcr()
    images = [
        TEST_DATA_ROOT / "images" / "00.jpg",
        TEST_DATA_ROOT / "images" / "02.jpg",
    ]

    # Test plain text batch
    batch_results = mocr.predict_batch(images, batch_size=2)
    assert len(batch_results) == 2
    assert batch_results[0] == "素直にあやまるしか"
    assert batch_results[1] == "実戦剣術も一流です"

    # Test confidence batch
    conf_results = mocr.predict_batch(images, batch_size=2, return_confidence=True)
    assert len(conf_results) == 2
    assert isinstance(conf_results[0], dict)
    assert conf_results[0]["text"] == "素直にあやまるしか"
    assert isinstance(conf_results[0]["confidence"], float)


def test_manga_page_pipeline():
    mocr = MangaOcr()
    pipeline = MangaPagePipeline(mocr_instance=mocr)
    img_path = TEST_DATA_ROOT / "images" / "00.jpg"

    # Mock detector returning two bounding boxes
    def mock_detector(img: Image.Image):
        return [
            (0, 0, img.width // 2, img.height),
            (img.width // 2, 0, img.width // 2, img.height),
        ]

    regions = pipeline.process_page(img_path, text_detector=mock_detector, return_confidence=True)
    assert isinstance(regions, list)
    assert len(regions) == 2
    assert "box" in regions[0]
    assert "text" in regions[0]
    assert "confidence" in regions[0]
