import os
import time
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class NebiusClient:
    def __init__(self):
        self.base_url = os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/")
        self.api_key = os.getenv("NEBIUS_API_KEY", "").strip()
        self.tokens_in = 0
        self.tokens_out = 0
        self.client = None

        if self.api_key and self.api_key != "mock":
            from openai import OpenAI
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
            )
        else:
            # Running in offline mock mode
            self.client = None

    def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4000,
        max_retries: int = 3
    ) -> str:
        """Calls Nebius Token Factory or falls back to an offline mock response if key is pending."""
        if not self.client:
            return self._mock_response(messages)

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                if response.usage:
                    self.tokens_in += response.usage.prompt_tokens or 0
                    self.tokens_out += response.usage.completion_tokens or 0

                return response.choices[0].message.content or ""
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(2 ** attempt)
        return ""

    def _mock_response(self, messages: List[Dict[str, str]]) -> str:
        """Simulates Nemotron output offline for local pipeline verification."""
        user_prompt = messages[-1]["content"] if messages else ""
        self.tokens_in += 120
        self.tokens_out += 60

        if "apply_discount" in user_prompt or "shopcalc" in user_prompt:
            return (
                "To fix the discount calculation, calculate the percentage discount instead of subtracting raw percent.\n\n"
                "FILE: shop/utils.py\n"
                "<<<<<<< SEARCH\n"
                "    return price - percent\n"
                "=======\n"
                "    return price * (1.0 - percent / 100.0)\n"
                ">>>>>>> REPLACE"
            )
        return "OK"

    def get_token_usage(self) -> Dict[str, int]:
        return {
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "tokens_total": self.tokens_in + self.tokens_out
        }