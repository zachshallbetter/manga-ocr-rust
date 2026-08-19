use manga_ocr_core::{post_process, EngineType, OcrEngine, OcrError, OcrMetadata, OcrResult};

pub struct OrtEngine {
    model_name: String,
}

impl OrtEngine {
    pub fn new(model_name: impl Into<String>) -> Self {
        Self {
            model_name: model_name.into(),
        }
    }
}

impl OcrEngine for OrtEngine {
    fn predict(&self, _image: &image::DynamicImage) -> Result<OcrResult, OcrError> {
        // Stub implementation demonstrating Rust ONNX integration contract
        Ok(OcrResult {
            text: post_process("…"),
            confidence: 0.985,
            token_probabilities: vec![0.98, 0.99],
            metadata: OcrMetadata {
                duration_ms: 4.2,
                model_name: self.model_name.clone(),
                engine_type: EngineType::BaseInt8Onnx,
            },
        })
    }

    fn predict_batch(
        &self,
        images: &[image::DynamicImage],
        _batch_size: usize,
    ) -> Result<Vec<OcrResult>, OcrError> {
        images.iter().map(|img| self.predict(img)).collect()
    }
}
