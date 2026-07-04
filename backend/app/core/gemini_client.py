from __future__ import annotations

import json
from typing import Any
import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class GeminiClientException(Exception):
    pass


class GeminiClient:
    """
    Reusable abstraction for Google's Gemini API.
    Handles raw HTTP requests to Gemini and wraps exceptions.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    async def generate_json(
        self,
        prompt: str,
        temperature: float = 0.7,
        response_schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Generates structured JSON content from the Gemini API.
        Validates HTTP status, JSON parsing, and wraps all httpx errors into GeminiClientException.
        """
        if not self.api_key:
            logger.warning("gemini_api_key_missing", message="GEMINI_API_KEY is not configured.")
            raise GeminiClientException("Gemini API key is not configured.")

        generation_config: dict[str, Any] = {
            "temperature": temperature,
            "response_mime_type": "application/json",
        }
        
        if response_schema:
            generation_config["response_schema"] = response_schema
            
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": generation_config
        }

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
                response = await client.post(
                    self.base_url,
                    params={"key": self.api_key},
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                if "candidates" not in data or not data["candidates"]:
                    raise GeminiClientException("No candidates returned from Gemini API.")
                
                content = data["candidates"][0].get("content", {})
                parts = content.get("parts", [])
                if not parts:
                    raise GeminiClientException("No text parts returned from Gemini API.")
                
                text_response = parts[0].get("text", "")
                if not text_response:
                    raise GeminiClientException("Empty text response from Gemini API.")
                
                return json.loads(text_response)

        except httpx.TimeoutException as exc:
            raise GeminiClientException(f"Gemini API timeout: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            raise GeminiClientException(f"Gemini API returned {exc.response.status_code}: {exc.response.text}") from exc
        except httpx.RequestError as exc:
            raise GeminiClientException(f"Gemini API request failed: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise GeminiClientException(f"Failed to parse Gemini API response as JSON: {exc}") from exc
        except Exception as exc:
            if isinstance(exc, GeminiClientException):
                raise
            raise GeminiClientException(f"Unexpected error communicating with Gemini API: {exc}") from exc
