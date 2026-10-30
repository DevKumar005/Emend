from abc import ABC, abstractmethod
from typing import List, Optional
from contracts.schemas import TestRun

class BaseRunner(ABC):
    """Abstract base class for test execution runners."""

    @abstractmethod
    def run(
        self,
        repo_path: Optional[str] = None,
        scope: str = "target",
        test_ids: Optional[List[str]] = None,
        timeout: int = 60
    ) -> TestRun:
        """Run tests against a target repository and return a structured TestRun."""
        pass

    def reset_repo(self) -> None:
        """Restores repository state."""
        pass
