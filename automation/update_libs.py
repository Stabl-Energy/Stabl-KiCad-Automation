#!/bin/python3

"""Process:
- create new lib
- push it
- run this script
"""
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import subprocess
from shutil import copy
from typing import Dict, List, Optional
from datetime import datetime


class LibKind(Enum):
    fp: str = "fp"
    sym: str = "sym"
    treeD: str = "3d"


@dataclass
class Library:
    kind: LibKind
    directory: Path
    extension: Optional[str] = None
    table_file: Optional[Path] = None


def update_repository(repository: Path):
    subprocess.run(f"git -C {repository.as_posix()} pull".split())


def update_repositories(repository_paths: Dict[str, Library]):
    for repository_path in repository_paths.values():
        update_repository(repository_path.directory)


def get_current_libs(lib_path: Path, extension: str):
    return list(lib_path.glob(f'*.{extension}'))


def filter_stabl(entry: str) -> bool:
    return "stabl" not in entry.lower()


def compose_lib_entry(lib_kind: str, lib_path: Path) -> str:
    return f'  (lib (name {lib_path.stem})(type "KiCad")(uri "$STABL_LIB/{lib_kind}/{lib_path.name}")(options "")(descr ""))\n'


def recreate_lib_table_content(table: list, sym_libs: list, lib_kind: str) -> List[str]:
    builtin_table = list(filter(filter_stabl, table))
    stabl_libs = [compose_lib_entry(lib_kind, lib) for lib in sym_libs]
    new_table = builtin_table[:-1]  # remove closing bracket
    new_table.extend(stabl_libs)
    new_table.append(')\n')
    return new_table


def update_lib_table(lib: Library, stabl_libs: List[Path]):
    with open(lib.table_file, "r") as f:
        table = f.readlines()
    new_table = recreate_lib_table_content(table, stabl_libs, lib.kind.value)
    with open(lib.table_file, "w") as f:
        f.writelines(new_table)


def backup_lib_table(table_location: Path):
    table_dir = table_location.parent
    backup_dir = table_dir/"backups"
    backup_dir.mkdir(exist_ok=True)
    copy(table_location, backup_dir/f"{table_location.stem}_backup_{datetime.now().strftime('%Y_%m_%d_%H_%M')}")


def synchronize_lib_table(lib: Library):
    current_libs = get_current_libs(lib.directory, lib.extension)
    backup_lib_table(lib.table_file)
    update_lib_table(lib, current_libs)


def update_lib_tables(repository_paths: Dict[str, Library]):
    synchronize_lib_table(repository_paths["sym"])
    synchronize_lib_table(repository_paths["fp"])


def update_libs():
    repository_base_path = Path("/home/max/Desktop/stabl_kicad_lib")
    lib_table_base_path = Path("/home/max/.config/kicad/6.0")
    repository_paths = {
        "sym": Library(LibKind.sym, repository_base_path/"sym", "kicad_sym", lib_table_base_path/"sym-lib-table"),
        "fp": Library(LibKind.fp, repository_base_path/"fp", "pretty", lib_table_base_path/"fp-lib-table"),
        "3d": Library(LibKind.treeD, repository_base_path/"3d"),
    }
    update_repositories(repository_paths)
    update_lib_tables(repository_paths)


if __name__ == "__main__":
    update_libs()
