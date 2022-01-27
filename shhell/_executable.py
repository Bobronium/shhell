from typing import Any, TypeVar

from ._command import Command

ExecutableT = TypeVar("ExecutableT", bound="Executable")


class Executable:
    def __init__(self, name: str) -> None:
        self.name = name

    def __call__(self, *args, **kwargs) -> Command:
        return Command(self.name, *args, **kwargs)

    @classmethod
    def from_dummy(cls: type[ExecutableT], dummy_function: Any) -> ExecutableT:
        return cls(dummy_function.__name__)
