"""OCR provider interface and implementations."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pytesseract
from PIL import Image
import io


class OCRProvider(ABC):
    """Abstract OCR provider."""

    @abstractmethod
    async def extract_text(self, image_bytes: bytes) -> Dict[str, Any]:
        """Extract text from image."""
        pass


class MockOCRProvider(OCRProvider):
    """Mock OCR for testing."""

    async def extract_text(self, image_bytes: bytes) -> Dict[str, Any]:
        return {
            "raw_text": "Mock OCR Result\nPatient Name: Test Patient\nMedication: Metformin 500mg\nDosage: Twice daily\nDate: 2026-08-28",
            "confidence": 0.92,
            "provider": "mock"
        }


class TesseractOCRProvider(OCRProvider):
    """Tesseract OCR for printed text."""

    async def extract_text(self, image_bytes: bytes) -> Dict[str, Any]:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image)
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) / 100 if confidences else 0.0

            return {
                "raw_text": text,
                "confidence": avg_confidence,
                "provider": "tesseract"
            }
        except Exception as e:
            raise Exception(f"Tesseract OCR failed: {e}")


class VisionOCRProvider(OCRProvider):
    """Vision API OCR for handwritten text."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def extract_text(self, image_bytes: bytes) -> Dict[str, Any]:
        # Placeholder for vision API integration
        # In real implementation, this would call a multimodal vision API
        return {
            "raw_text": "Handwritten text extraction requires vision API configuration",
            "confidence": 0.0,
            "provider": "vision",
            "warning": "Vision API not configured"
        }


def get_ocr_provider() -> OCRProvider:
    """Get configured OCR provider."""
    from app.core.config import settings

    provider_type = settings.OCR_PROVIDER.lower()

    if provider_type == "tesseract":
        return TesseractOCRProvider()
    elif provider_type == "vision":
        if settings.VISION_API_KEY:
            return VisionOCRProvider(settings.VISION_API_KEY)
        return TesseractOCRProvider()  # Fallback
    else:
        return MockOCRProvider()
