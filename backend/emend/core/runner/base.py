from abc import ABC, abstractmethod
from typing import List, Optional
from contracts.schemas import TestRun

class BaseRunner(ABC):
    @abstractmethod
    def run(
        self,
        repo_path: str,
        scope: str,
        test_ids: Optional[List[str]] = None,
        timeout: int = 60
    ) -> TestRun:
        """Run tests against a target repository and return a structured TestRun."""
        pass