"""Speech recognition provider interface and implementations."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import httpx
from app.core.config import settings


class SpeechRecognitionProvider(ABC):
    """Abstract base class for speech recognition providers."""

    @abstractmethod
    async def transcribe(
        self,
        audio_file: bytes,
        language_code: str,
        mime_type: str
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text.

        Returns:
            {
                "transcript": str,
                "confidence": float,
                "language": str,
                "provider": str
            }
        """
        pass


class MockSpeechRecognitionProvider(SpeechRecognitionProvider):
    """Mock provider for testing."""

    async def transcribe(
        self,
        audio_file: bytes,
        language_code: str,
        mime_type: str
    ) -> Dict[str, Any]:
        """Mock transcription."""
        return {
            "transcript": "Mock transcription for testing purposes",
            "confidence": 0.95,
            "language": language_code,
            "provider": "mock"
        }


class SarvamSpeechRecognitionProvider(SpeechRecognitionProvider):
    """Sarvam AI speech recognition provider."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.sarvam.ai/speech-to-text"

    async def transcribe(
        self,
        audio_file: bytes,
        language_code: str,
        mime_type: str
    ) -> Dict[str, Any]:
        """Transcribe using Sarvam AI."""
        if not self.api_key:
            raise ValueError("Sarvam API key not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        files = {
            "file": ("audio.wav", audio_file, mime_type)
        }

        data = {
            "language_code": language_code
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    files=files,
                    data=data
                )
                response.raise_for_status()
                result = response.json()

                return {
                    "transcript": result.get("transcript", ""),
                    "confidence": result.get("confidence", 0.0),
                    "language": language_code,
                    "provider": "sarvam"
                }

            except httpx.TimeoutException:
                raise Exception("Speech recognition service timeout")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    raise Exception("Rate limit exceeded")
                elif e.response.status_code == 401:
                    raise Exception("Invalid API credentials")
                else:
                    raise Exception(f"Speech recognition failed: {e}")
            except Exception as e:
                raise Exception(f"Speech recognition error: {e}")


def get_speech_provider() -> SpeechRecognitionProvider:
    """Get configured speech recognition provider."""
    provider_type = settings.SPEECH_PROVIDER.lower()

    if provider_type == "sarvam":
        if not settings.SARVAM_API_KEY:
            raise ValueError("SARVAM_API_KEY not configured")
        return SarvamSpeechRecognitionProvider(settings.SARVAM_API_KEY)
    else:
        return MockSpeechRecognitionProvider()
