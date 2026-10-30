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
                "FILE: shop/utils.py\n"
                "<<<<<<< SEARCH\n"
                "    return price - percent\n"
                "=======\n"
                "    return price * (1.0 - percent / 100.0)\n"
                ">>>>>>> REPLACE"
            )

        if "round_price" in user_prompt or "billing" in user_prompt or "test_pricing" in user_prompt:
            if "Previous attempt failed" in user_prompt or "Regression" in user_prompt:
                # Attempt 2: Symmetric decimal rounding fixes pricing and negative refunds
                return (
                    "FILE: billing/utils.py\n"
                    "<<<<<<< SEARCH\n"
                    "    return round(x, 2)\n"
                    "=======\n"
                    "    from decimal import Decimal, ROUND_HALF_UP\n"
                    "    return float(Decimal(str(x)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))\n"
                    ">>>>>>> REPLACE"
                )
            else:
                # Attempt 1: Naive fix breaks negative refunds in refunds.py
                return (
                    "FILE: billing/utils.py\n"
                    "<<<<<<< SEARCH\n"
                    "    return round(x, 2)\n"
                    "=======\n"
                    "    return int(x * 100 + 0.5) / 100.0\n"
                    ">>>>>>> REPLACE"
                )

        return "OK"

    def get_token_usage(self) -> Dict[str, int]:
        return {
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "tokens_total": self.tokens_in + self.tokens_out
        }