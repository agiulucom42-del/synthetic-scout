from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class TestCase:
    name: str
    func: Callable[[], None]
    tags: List[str] = field(default_factory=list)


class TestRegistry:
    def __init__(self) -> None:
        self._tests: Dict[str, TestCase] = {}

    def register(self, name: str, func: Callable[[], None], tags: Optional[List[str]] = None) -> None:
        tag_list = list(tags) if tags else []
        if name in self._tests:
            raise ValueError(f"Test name already registered: {name}")
        self._tests[name] = TestCase(name=name, func=func, tags=tag_list)

    def all_tests(self) -> List[TestCase]:
        return list(self._tests.values())

    def by_tag(self, tags: List[str]) -> List[TestCase]:
        if not tags:
            return self.all_tests()
        tag_set = set(tags)
        return [test_case for test_case in self._tests.values() if tag_set.intersection(test_case.tags)]

    def exclude_tag(self, tests: List[TestCase], exclude_tags: List[str]) -> List[TestCase]:
        if not exclude_tags:
            return tests
        exclude_set = set(exclude_tags)
        return [test_case for test_case in tests if not exclude_set.intersection(test_case.tags)]

    def list_tests(self) -> List[Dict[str, Any]]:
        return [{"name": test_case.name, "tags": test_case.tags} for test_case in self._tests.values()]


REGISTRY = TestRegistry()


def test(name: Optional[str] = None, tags: Optional[List[str]] = None) -> Callable[[Callable[[], None]], Callable[[], None]]:
    def decorator(fn: Callable[[], None]) -> Callable[[], None]:
        t_name = name if name else fn.__name__
        REGISTRY.register(t_name, fn, tags or [])
        return fn

    return decorator
