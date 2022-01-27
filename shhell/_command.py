from typing import Any

from ._result import ExecutionResult
from ._typehints import CommandT


class Command:
    """
    Remembers executable and given args.
    Allows to execute the command and retrieve the result.
    May be used as an argument value for another shhell command.
    """

    def __init__(self, executable: str, *args: Any, **kwargs: Any) -> None:
        """Just remember given args, we're going to build command when we actually will need to"""
        self.executable = executable
        self.args = args
        self.kwargs = kwargs

    def run(self: CommandT, *args, **kwargs) -> ExecutionResult[CommandT]:
        """Execute command in sync mode and return it's result"""
        raise NotImplementedError('shhellno')

    async def arun(self: CommandT) -> ExecutionResult[CommandT]:
        """Execute command in async mode and return it's result"""
        raise NotImplementedError('shhellno')

    def __await__(self):
        """Allow to simply await CMD instance"""
        return self.arun().__await__()

    def __or__(self, other):
        ...

    def __le__(self, other):
        ...

    ...
