from typing import Dict, Any
from abc import ABC, abstractmethod

from report.reporter import TestResult


class Plugin(ABC):
    @abstractmethod
    def on_start(self, context: Dict[str, Any]) -> None:
        ...

    @abstractmethod
    def on_test_result(self, result: TestResult) -> None:
        ...

    @abstractmethod
    def on_finish(self, summary: Dict[str, Any]) -> None:
        ...
