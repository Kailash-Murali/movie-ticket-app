import json
import logging
import os
import requests
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger("cinemate.ai")

class LLMClient:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY or settings.LLM_API_KEY
        self.model = settings.LLM_MODEL
        self.provider = settings.LLM_PROVIDER.lower()

    def generate_json(self, prompt: str, system_prompt: str) -> Optional[Dict[str, Any]]:
        """
        Sends request to LLM provider (Gemini, OpenAI, OpenRouter, or mock) and expects parsed JSON dict return.
        """
        if not self.api_key or self.api_key in ["mock-or-your-api-key", "mock-key", "your-openrouter-api-key"]:
            logger.info("Using built-in LLM parser engine (no API key configured).")
            return None

        if self.provider == "openrouter":
            return self._call_openrouter_json(prompt, system_prompt)
        elif self.provider == "gemini":
            return self._call_gemini_json(prompt, system_prompt)
        elif self.provider == "openai":
            return self._call_openai_json(prompt, system_prompt)
        else:
            logger.warning(f"Unknown provider '{self.provider}'. Falling back to rule parser.")
            return None

    def generate_text(self, prompt: str, system_prompt: str) -> str:
        """
        Sends request to LLM provider for text response.
        """
        if not self.api_key or self.api_key in ["mock-or-your-api-key", "mock-key", "your-openrouter-api-key"]:
            return ""

        if self.provider == "openrouter":
            return self._call_openrouter_text(prompt, system_prompt) or ""
        elif self.provider == "gemini":
            return self._call_gemini_text(prompt, system_prompt) or ""
        elif self.provider == "openai":
            return self._call_openai_text(prompt, system_prompt) or ""
        return ""

    def _call_openrouter_json(self, prompt: str, system_prompt: str) -> Optional[Dict[str, Any]]:
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://cinemate-ai.local",
                "X-Title": "CineMate AI",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model if "/" in self.model else f"google/{self.model}",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.1
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                return json.loads(content)
            else:
                logger.error(f"OpenRouter API call failed ({resp.status_code}): {resp.text}")
                return None
        except Exception as e:
            logger.error(f"Error calling OpenRouter JSON API: {e}")
            return None

    def _call_openrouter_text(self, prompt: str, system_prompt: str) -> Optional[str]:
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://cinemate-ai.local",
                "X-Title": "CineMate AI",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model if "/" in self.model else f"google/{self.model}",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.4
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            return None
        except Exception as e:
            logger.error(f"Error calling OpenRouter text API: {e}")
            return None

    def _call_gemini_json(self, prompt: str, system_prompt: str) -> Optional[Dict[str, Any]]:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {"role": "user", "parts": [{"text": f"{system_prompt}\n\nUSER PROMPT: {prompt}"}]}
                ],
                "generationConfig": {
                    "response_mime_type": "application/json",
                    "temperature": 0.1
                }
            }
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
            else:
                logger.error(f"Gemini API call failed with status {resp.status_code}: {resp.text}")
                return None
        except Exception as e:
            logger.error(f"Error calling Gemini LLM API: {e}")
            return None

    def _call_gemini_text(self, prompt: str, system_prompt: str) -> Optional[str]:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {"role": "user", "parts": [{"text": f"{system_prompt}\n\nUSER PROMPT: {prompt}"}]}
                ],
                "generationConfig": {"temperature": 0.4}
            }
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            return None
        except Exception as e:
            logger.error(f"Error calling Gemini text API: {e}")
            return None

    def _call_openai_json(self, prompt: str, system_prompt: str) -> Optional[Dict[str, Any]]:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model if "gpt" in self.model else "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.1
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                return json.loads(content)
            return None
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return None

    def _call_openai_text(self, prompt: str, system_prompt: str) -> Optional[str]:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model if "gpt" in self.model else "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.4
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            return None
        except Exception as e:
            logger.error(f"Error calling OpenAI text API: {e}")
            return None

llm_client = LLMClient()
