from pathlib import Path
from typing import List

import pytest

import automation.update_libs as program


test_table_content = [
    '(fp_lib_table',
    '(lib(name "Audio_Module")(type "KiCad")(uri "${KICAD6_FOOTPRINT_DIR}/Audio_Module.pretty")(options "")(descr "Audio Module footprints"))',
    '(lib(name "Battery")(type "KiCad")(uri "${KICAD6_FOOTPRINT_DIR}/Battery.pretty")(options "")(descr "Battery and battery holder footprints"))',
    ')'
]


def is_valid_fp_lib_table(lib_table: List[str]) -> bool:
    return all([
        lib_table[0].strip() == "(fp_lib_table",
        lib_table[-1].strip() == ")"
    ])


def is_valid_lib_entry(lib_entry: str) -> bool:
    ...


def test_recreate_lib_table_content():
    stabl_libs = [
        Path("stabl_lib/fp/stabl_emi.pretty")
    ]
    new_table = program.recreate_lib_table_content(test_table_content, stabl_libs, "fp")
    for entry in stabl_libs:
        assert any([entry.stem in table_entry for table_entry in new_table])
    for entry in test_table_content:
        assert entry in new_table
    assert len(set(new_table)) == len(new_table)  # check for duplicates
    assert is_valid_fp_lib_table(new_table)


def test_compose_lib_entry() -> None:
    new_lib_name = "stabl_emi"
    new_lib = Path("stabl_lib/fp/stabl_emi.pretty")
    new_lib_entry = program.compose_lib_entry("fp", new_lib)
    assert new_lib_entry == f'  (lib (name {new_lib_name})(type "KiCad")(uri "$STABL_LIB/fp/{new_lib_name}.pretty")(options "")(descr ""))\n'
