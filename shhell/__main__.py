import logging
import os
from itertools import chain
from keyword import iskeyword
from pathlib import Path
from textwrap import dedent, indent


__all__ = ["ALIAS_TRANSLATIONS", "SHHELL_DIR", "EXECUTABLES_DIR"]

ALIAS_TRANSLATIONS = {
    # >>> 'i-dunno-c++-but-i-love-python3.10'.translate(ALIAS_TRANSLATIONS)
    # i_dunno_cpp_but_i_love_python3_10
    ord(char): replacement
    for char, replacement in (
        (".", "_"),
        ("-", "_"),
        ("+", "p"),
    )
}
SHHELL_DIR = Path(__file__).parent
EXECUTABLES_DIR = SHHELL_DIR / "_executables"
IMPORTS_NOTE = """
# The next section of the file contains only automatically generated code.
# These imports list should be defined only inside of __init__.pyi, 
# but I found that PyCharm is not smart enough to take it to the account :/
# On the bright side, however, only one of all the imports below will be executed.
""".strip()
IMPORTS_NOTE_FIRST_LINE, _ = IMPORTS_NOTE.split("\n", maxsplit=1)


def generate_stats(may_be_declared_as_attrs, may_be_aliased_as_attrs, unable_to_declare) -> str:
    chars = " ".join(map(chr, ALIAS_TRANSLATIONS))
    unable_to_declare = " ".join(map(str.strip, unable_to_declare))
    return dedent(
        f"""
        Created {len(may_be_declared_as_attrs)} 1:1 references
        Created {len(may_be_aliased_as_attrs)} references, replacing characters like {chars}
        Were not able to create {len(unable_to_declare)} references: {unable_to_declare}
        """
    ).strip()


def main():
    print("Generating dummy files and imports...")

    unable_to_declare = {}
    may_be_declared_as_attrs = {}
    may_be_aliased_as_attrs = {}

    for path in map(Path, os.getenv("PATH").split(":")):
        if not path.exists() or not path.is_dir():
            continue

        for name, executable in ((p.name, p) for p in path.iterdir() if os.access(p, os.X_OK)):
            if name.isidentifier() and not iskeyword(name):
                may_be_declared_as_attrs[name] = executable
            elif (
                allowed_name := name.translate(ALIAS_TRANSLATIONS)
            ).isidentifier() and allowed_name not in may_be_declared_as_attrs.keys() | {
                "__getattr__"
            }:
                if iskeyword(allowed_name):
                    allowed_name = f"{allowed_name}_"
                may_be_aliased_as_attrs[allowed_name] = executable
            else:
                unable_to_declare[name] = ...

    imports = []
    for name, executable in chain(
        may_be_declared_as_attrs.items(), may_be_aliased_as_attrs.items()
    ):
        assert name.isidentifier()
        module = EXECUTABLES_DIR / f"{name}.py"
        imports.append(f"from ._executables.{name} import {name}  # noqa\n")
        logging.debug(f"Writing dummy for {executable} in {module.relative_to(Path.cwd())}")
        module.write_text(
            dedent(
                f'''
                """This module is generated to provide autocomplete for {executable.name}"""
                from .._executable import Executable
                from .._command import Command


                @Executable.from_dummy
                def {name}(*args, **kwargs) -> Command:
                    """{executable}"""
                '''
            ).strip() + '\n',
        )
    shhell_init_path = SHHELL_DIR / "__init__.py"
    logging.debug(f"Adding dummy imports to {shhell_init_path.relative_to('/', Path.cwd())}")

    stats = generate_stats(may_be_declared_as_attrs, may_be_aliased_as_attrs, unable_to_declare)

    with open(shhell_init_path, "r+") as shhell_init_file:
        line_start = 0
        for line in shhell_init_file:
            if line.strip() == IMPORTS_NOTE_FIRST_LINE:
                shhell_init_file.seek(line_start)
                break
            else:
                line_start += len(line)
        else:
            shhell_init_file.write("\n\n")

        shhell_init_file.write(
            f"""
{IMPORTS_NOTE}

{indent(stats, '# ')}
from typing import TYPE_CHECKING  as _TYPE_CHECKING # noqa

if _TYPE_CHECKING:
{indent("".join(imports), ' ' * 4)}
            """.strip() + '\n'
        )
        shhell_init_file.truncate(shhell_init_file.tell())
    print(
        f"Done! You now have autocompletion for {len(imports)} executables ✨\n\n"
        f"Some stats:\n{stats}"
    )


if __name__ == "__main__":
    main()
