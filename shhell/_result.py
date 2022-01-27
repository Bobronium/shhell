from typing import Generic

from ._typehints import CommandT


class ExecutionResult(Generic[CommandT]):
    """
    Dunno how I want result to look like yet. We'll see.
    """

    command: CommandT
