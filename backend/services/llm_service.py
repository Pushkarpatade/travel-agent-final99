"""TravelPilot Resilient Multi-Provider LLM Service.

Supports:
1. Google Gemini (google.genai SDK)
2. Groq (ultra-low latency Llama 3.3 / Llama 3.1 models)
3. OpenAI (GPT-4o, GPT-4o-mini)
4. Intelligent Fallback Engine (gracefully synthesizes structured data if external LLMs are unreachable)
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from backend.config import settings

logger = logging.getLogger("travelpilot.llm_service")

class ResilientLLMService:
    def __init__(self):
        self.provider: Optional[str] = None
        self._init_clients()

    def _init_clients(self):
        # 1. Try Gemini
        self.gemini_key = settings.GEMINI_API_KEY
        self.gemini_client = None
        if self.gemini_key and len(self.gemini_key.strip()) > 10:
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=self.gemini_key)
                self.provider = "gemini"
                logger.info("Initialized Google Gemini client.")
            except Exception as e:
                logger.warning(f"Could not initialize Gemini Client: {e}")

        # 2. Try Groq
        self.groq_key = settings.GROQ_API_KEY
        self.groq_client = None
        if self.groq_key and len(self.groq_key.strip()) > 10:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_key)
                if not self.provider:
                    self.provider = "groq"
                logger.info("Initialized Groq client.")
            except Exception as e:
                logger.warning(f"Could not initialize Groq Client: {e}")

        # 3. Try OpenAI
        self.openai_key = settings.OPENAI_API_KEY
        self.openai_client = None
        if self.openai_key and len(self.openai_key.strip()) > 10:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.openai_key)
                if not self.provider:
                    self.provider = "openai"
                logger.info("Initialized OpenAI client.")
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI Client: {e}")

        if not self.provider:
            logger.info("No active external LLM key provided. Intelligent Fallback Engine active.")

    def is_configured(self) -> bool:
        return self.provider is not None

    def get_active_provider(self) -> str:
        return self.provider or "Intelligent Fallback Engine"

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generates natural text across providers with graceful fallback."""
        # 1. Gemini
        if self.gemini_client:
            for model_name in [settings.GEMINI_MODEL, "gemini-3.6-flash", "gemini-3.8-flash", "gemini-2.5-flash"]:
                try:
                    full_content = f"{system_instruction or ''}\n\n{prompt}".strip()
                    res = self.gemini_client.models.generate_content(
                        model=model_name,
                        contents=full_content
                    )
                    if res and res.text:
                        return res.text.strip()
                except Exception as e:
                    logger.warning(f"Gemini {model_name} failed: {e}")

        # 2. Groq
        if self.groq_client:
            for model_name in [settings.GROQ_MODEL, "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
                try:
                    messages = []
                    if system_instruction:
                        messages.append({"role": "system", "content": system_instruction})
                    messages.append({"role": "user", "content": prompt})
                    chat_completion = self.groq_client.chat.completions.create(
                        messages=messages,
                        model=model_name,
                        temperature=0.3
                    )
                    return chat_completion.choices[0].message.content.strip()
                except Exception as e:
                    logger.warning(f"Groq {model_name} failed: {e}")

        # 3. OpenAI
        if self.openai_client:
            try:
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})
                chat_completion = self.openai_client.chat.completions.create(
                    messages=messages,
                    model="gpt-4o-mini",
                    temperature=0.3
                )
                return chat_completion.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"OpenAI call failed: {e}")

        return ""

    def generate_json(self, prompt: str, system_instruction: Optional[str] = None) -> Dict[str, Any]:
        """Generates structured JSON across providers with automatic JSON markdown stripping."""
        json_instruction = (
            f"{system_instruction or ''}\n\n"
            "CRITICAL REQUIREMENT: Return ONLY valid, parseable JSON. Do not enclose in markdown codeblocks."
        ).strip()

        raw_text = self.generate_text(prompt, system_instruction=json_instruction)
        if raw_text:
            return self._parse_json_response(raw_text)

        return {}

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        clean_text = text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()

        try:
            return json.loads(clean_text)
        except Exception:
            try:
                start = clean_text.find("{")
                end = clean_text.rfind("}")
                if start != -1 and end != -1:
                    return json.loads(clean_text[start:end+1])
            except Exception:
                pass
            return {}

# Singleton
llm_service = ResilientLLMService()
