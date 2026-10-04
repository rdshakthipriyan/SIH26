"""Text-to-speech provider interface and implementations."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import httpx
import base64
from app.core.config import settings


class TextToSpeechProvider(ABC):
    """Abstract base class for TTS providers."""

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        language_code: str,
        voice: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesize text to speech.

        Returns:
            {
                "audio_base64": str,
                "duration_seconds": float,
                "provider": str,
                "status": "success"
            }
        """
        pass


class MockTextToSpeechProvider(TextToSpeechProvider):
    """Mock TTS provider for testing / demo mode.

    Produces a minimal valid WAV file (44-byte header + ~0.1s silence at 16kHz mono).
    Browsers can play this without errors.
    """

    async def synthesize(
        self,
        text: str,
        language_code: str,
        voice: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mock synthesis — minimal valid WAV silence so browsers don't error."""
        # WAV header: 44 bytes, PCM 16-bit mono 16kHz
        # RIFF header + fmt chunk + data chunk header (no actual samples)
        wav_header = bytes([
            # "RIFF"
            0x52, 0x49, 0x46, 0x46,
            # file size (little-endian): 44 + 0 samples = 36 = 0x24
            0x24, 0x00, 0x00, 0x00,
            # "WAVE"
            0x57, 0x41, 0x56, 0x45,
            # "fmt "
            0x66, 0x6D, 0x74, 0x20,
            # fmt chunk size: 16
            0x10, 0x00, 0x00, 0x00,
            # audio format: 1 = PCM
            0x01, 0x00,
            # num channels: 1 = mono
            0x01, 0x00,
            # sample rate: 16000
            0x00, 0x3E, 0x00, 0x00,
            # byte rate: 32000
            0x00, 0x7D, 0x00, 0x00,
            # block align: 2
            0x02, 0x00,
            # bits per sample: 16
            0x10, 0x00,
            # "data"
            0x64, 0x61, 0x74, 0x61,
            # data size: 0 bytes of audio
            0x00, 0x00, 0x00, 0x00,
        ])
        return {
            "audio_base64": base64.b64encode(wav_header).decode(),
            "duration_seconds": 0.1,
            "provider": "mock",
            "status": "success",
            "language_code": language_code,
            "demo_mode": True,
        }


class SarvamBulbulTextToSpeechProvider(TextToSpeechProvider):
    """Sarvam AI Bulbul TTS provider."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.sarvam.ai/text-to-speech"

    async def synthesize(
        self,
        text: str,
        language_code: str,
        voice: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synthesize using Sarvam Bulbul."""
        if not self.api_key:
            raise ValueError("Sarvam API key not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "text": text,
            "language_code": language_code,
            "speaker": voice or "default"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()

                audio_base64 = result.get("audio", "")
                if not audio_base64:
                    # Audio might be in different format
                    audio_base64 = base64.b64encode(response.content).decode()

                return {
                    "audio_base64": audio_base64,
                    "duration_seconds": result.get("duration", 0.0),
                    "provider": "sarvam",
                    "status": "success"
                }

            except httpx.TimeoutException:
                return {
                    "audio_base64": None,
                    "duration_seconds": 0.0,
                    "provider": "sarvam",
                    "status": "unavailable",
                    "message": "TTS service timeout"
                }
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    return {
                        "audio_base64": None,
                        "provider": "sarvam",
                        "status": "unavailable",
                        "message": "Rate limit exceeded"
                    }
                else:
                    return {
                        "audio_base64": None,
                        "provider": "sarvam",
                        "status": "unavailable",
                        "message": f"TTS failed: {e}"
                    }
            except Exception as e:
                return {
                    "audio_base64": None,
                    "provider": "sarvam",
                    "status": "unavailable",
                    "message": f"TTS error: {e}"
                }


def get_tts_provider() -> TextToSpeechProvider:
    """Get configured TTS provider."""
    provider_type = settings.TTS_PROVIDER.lower()

    if provider_type == "sarvam":
        if not settings.SARVAM_API_KEY:
            return MockTextToSpeechProvider()  # Fallback to mock
        return SarvamBulbulTextToSpeechProvider(settings.SARVAM_API_KEY)
    else:
        return MockTextToSpeechProvider()
