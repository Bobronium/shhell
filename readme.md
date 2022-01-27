# Shhell

Subprocess replacement ~~done right~~ with fancy API to build commands, autocompletion and typing support ✨

I was not satisfied with API of subprocess/sh/plumbum, so I decided to at least define how the perfect API should look like for me. 

Coming soon, sometime or just never.

How I want API to look like:
```py
import shhell

shhell.sh(c=shhell.curl(*'fsSL', 'https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh')).run()
```
which will be translated to:
```shell
sh -c "$(curl -fsSL 'https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh')"
```

`shhell.<cmd>(...)` will produce an instance of special class, which can invoke and get result from command both synchronously and asynchronously, allowing flexibility:  
```py
import asyncio
import shhell

OUTPUT_FILE = "example.mp4"

async def download():
    await shhell.curl(
        *'fsSL',
        "https://file-examples-com.github.io/uploads/2017/04/file_example_MP4_1920_18MG.mp4",
        output=OUTPUT_FILE
    )

async def print_file_size():
    while True:
        await shhell.echo(f'\t{await shhell.stat(OUTPUT_FILE, printf="%s")}')
        await asyncio.sleep(0.1)

asyncio.run(
    asyncio.wait(
        [
            asyncio.create_task(download()), 
            asyncio.create_task(print_file_size())
        ],
        return_when=asyncio.FIRST_COMPLETED
    )
)
```

## Pipes, redirects, subshells?
I like how plumbum deos this, i.e. using python magic methods allowing `|`, `>` support. In fact, if I'm going to write this library, I'm going to steal a lot of ideas from plumbum, changing little things that I don't like.   

## How autocompletion would even work?
Code generation, of course! However, it's not going to be easy, if achievable at all...

One of the options is generating signatures upon package build for executables available in PATH (expected args, types, docs) from -h/--help/man output for the command for linux/macOS.
This option is only viable on CI/CD stages, however. 

There should be api available for users to generate code structures for their own non-standard executables.

    Note: all the generated code will serve only cosmetic purpose, whether a signature was generated for a specific executable or not, the runtime result should always remain the same.

So `shhell/executables/cowsay.py` would look like this:
```py
from typing import Any, Literal
from shhell.command import Command
from shhell.executable import Executable

@Executable.from_dummy
def cowsay(
    *args: Literal["b", "d", "g", "p", "s", "t", "w", "y", "l", "n"],
    # __message this is positional only optional argument
    __message: str = ...,
    # these arguments are keyword only (e='??' will be converted to -e '??')
    e: Any = "eyes",
    f: Any = "cowfile",
    T: Any = "tongue",
    W: Any = "wrapcolumn",
) -> Command:
    """
    cow{say,think} version 3.03, (c) 1999 Tony Monroe
    Usage: cowsay [-bdgpstwy] [-h] [-e eyes] [-f cowfile]
          [-l] [-n] [-T tongue] [-W wrapcolumn] [message]
    """
...
```
