import os
from typing import Literal

ModelTask = Literal["repair", "classification", "summary", "research"]

class ModelRouter:
    """Routes LLM tasks to appropriate NVIDIA Nemotron models served on Nebius Token Factory."""

    def __init__(self):
        self.model_repair = os.environ.get(
            "MODEL_REPAIR", "nvidia/nemotron-3-super-120b-a12b"
        )
        self.model_fast = os.environ.get(
            "MODEL_FAST", "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"
        )

    def route(self, task: ModelTask) -> str:
        """Returns the appropriate model identifier based on task complexity and budget."""
        if task in ("repair", "research"):
            # Heavy reasoning tasks route to Nemotron Super 120B
            return self.model_repair
        else:
            # Fast summarization, classification, ranking route to Nemotron Nano / Lightning
            return self.model_fast

    def describe(self) -> dict:
        return {
            "repair_model": self.model_repair,
            "fast_model": self.model_fast,
            "provider": "Nebius Token Factory (NVIDIA Nemotron)",
            "base_url": os.environ.get("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/")
        }
