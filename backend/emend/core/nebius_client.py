import os
import re
import time
from typing import List, Dict, Any, Optional, Tuple, Union
from dotenv import load_dotenv

load_dotenv()

class NebiusClient:
    """Client for Nebius Token Factory serving NVIDIA Nemotron models.
    Supports live Token Factory API inference and offline simulated mode.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.api_key = (api_key or os.getenv("NEBIUS_API_KEY", "")).strip()
        self.base_url = base_url or os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/")
        self.is_live = bool(self.api_key and not self.api_key.startswith("mock") and not self.api_key.startswith("your_"))
        
        self.tokens_in = 0
        self.tokens_out = 0
        self.total_tokens_in = 0
        self.total_tokens_out = 0
        
        self.client = None
        if self.is_live:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    base_url=self.base_url,
                    api_key=self.api_key,
                    timeout=60.0
                )
            except Exception as e:
                print(f"[NebiusClient] Warning: Could not initialize OpenAI client: {e}. Falling back to offline mode.")
                self.client = None
                self.is_live = False

    def strip_reasoning(self, text: str) -> str:
        """Nemotron models may return extended reasoning traces (<think> tags)."""
        cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        cleaned = re.sub(r"```reasoning.*?```", "", cleaned, flags=re.DOTALL)
        return cleaned.strip()

    def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4000,
        max_retries: int = 3,
        return_tokens: bool = False,
        task_hint: Optional[str] = None,
        attempt: int = 1,
    ) -> Union[str, Tuple[str, int, int]]:
        """Calls Nebius Token Factory or falls back to an offline simulated response."""
        if self.is_live and self.client:
            backoff = 1.0
            last_err = None
            for retry_i in range(max_retries):
                try:
                    resp = self.client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    raw_content = resp.choices[0].message.content or ""
                    cleaned = self.strip_reasoning(raw_content)

                    tin = resp.usage.prompt_tokens if resp.usage else 800
                    tout = resp.usage.completion_tokens if resp.usage else max(len(cleaned) // 4, 1)

                    self.tokens_in += tin
                    self.tokens_out += tout
                    self.total_tokens_in += tin
                    self.total_tokens_out += tout

                    if return_tokens:
                        return cleaned, tin, tout
                    return cleaned
                except Exception as e:
                    last_err = e
                    time.sleep(backoff)
                    backoff *= 2.0
            print(f"[NebiusClient] Live API error after {max_retries} attempts: {last_err}. Using offline simulation.")

        # Offline deterministic simulation
        content, tin, tout = self._mock_response(messages, attempt=attempt)
        self.tokens_in += tin
        self.tokens_out += tout
        self.total_tokens_in += tin
        self.total_tokens_out += tout

        if return_tokens:
            return content, tin, tout
        return content

    def _mock_response(self, messages: List[Dict[str, str]], attempt: int = 1) -> Tuple[str, int, int]:
        user_content = "\n".join([m.get("content", "") for m in messages])

        if "apply_discount" in user_content or "shop" in user_content or "shopcalc" in user_content:
            rationale = "Bug: apply_discount subtracts percent directly rather than computing percentage."
            patch = (
                "FILE: shop/utils.py\n"
                "<<<<<<< SEARCH\n"
                "    return price - percent\n"
                "=======\n"
                "    return price * (1.0 - percent / 100.0)\n"
                ">>>>>>> REPLACE"
            )
            return f"{rationale}\n\n{patch}", 350, 180

        elif "round_price" in user_content or "billing" in user_content or "pricing" in user_content:
            has_regression_feedback = (attempt > 1) or ("previous attempt failed" in user_content.lower()) or ("regression" in user_content.lower())
            if not has_regression_feedback:
                # Attempt 1: Naive fix (causes downstream regression in refunds.py)
                rationale = "Attempt 1: Applying standard commercial half-up rounding formula."
                patch = (
                    "FILE: billing/utils.py\n"
                    "<<<<<<< SEARCH\n"
                    "    return round(x, 2)\n"
                    "=======\n"
                    "    return int(x * 100 + 0.5) / 100.0\n"
                    ">>>>>>> REPLACE"
                )
                return f"{rationale}\n\n{patch}", 420, 160
            else:
                # Attempt 2: Symmetric decimal fix (preserves refunds and pricing)
                rationale = "Attempt 2: Regression in refunds detected. Using Python decimal with ROUND_HALF_UP symmetrically."
                patch = (
                    "FILE: billing/utils.py\n"
                    "<<<<<<< SEARCH\n"
                    "    return round(x, 2)\n"
                    "=======\n"
                    "    from decimal import Decimal, ROUND_HALF_UP\n"
                    "    d = Decimal(str(x))\n"
                    "    return float(d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))\n"
                    ">>>>>>> REPLACE"
                )
                return f"{rationale}\n\n{patch}", 550, 220

        elif "scheduler" in user_content or "workday" in user_content or "holiday" in user_content:
            rationale = (
                "The corporate holiday calendar data is missing and cannot be derived statically from code alone. "
                "Unable to resolve external business policy without authoritative corporate calendar input."
            )
            return rationale, 400, 120

        return "OK", 50, 50

    def get_token_usage(self) -> Dict[str, int]:
        return {
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "tokens_total": self.tokens_in + self.tokens_out
        }
