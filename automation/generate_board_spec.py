from dataclasses import dataclass
from pathlib import Path
from typing import List
from jinja2 import FileSystemLoader, Environment
from latex import build_pdf


@dataclass
class PcbSpecs_mm:
    minimum_trace_width: float
    minimum_clearance: float
    minimum_drill_size: float


def create_board_spec(project_path: Path, output_subdir: Path = Path("outputs")) -> None:
    specs = _get_specs_from_report(_read_report_file(project_path / output_subdir))
    specs.update(_import_text_variables(project_path))
    content = _render_template(specs)
    _export_pdf(content, Path("spec.pdf"))


def _read_report_file(output_path: Path) -> List[str]:
    try:
        report_file = next(output_path.glob("*-report.txt"))
    except StopIteration:
        print(f"No report file found in {output_path.as_posix()}")
        exit(-1)
    with open(report_file, 'r') as rf:
        return rf.readlines()


def _get_specs_from_report(report: List[str]) -> dict:
    specs = {'Board size': None, 'Layers': None, 'Thickness': None, 'Material': None, 'Solder mask': None, 'Silk screen': None, 'Track width': None,
             'Clearance': None, 'Drill': None, ' Via': None, 'Outer Annular Ring': None}
    for key in specs.keys():
        for line in report:
            if key in line:
                try:
                    pair = line.split(":", 1)
                    specs[key] = pair[1].strip()
                except IndexError:
                    print(f"cannot extract {key} from {line}")
    return specs


def _import_text_variables(project_path: Path) -> dict:
    return {}


def _render_template(specs: dict) -> str:
    p = Path(__file__).parent
    env = Environment(loader=FileSystemLoader(p))
    template = env.get_template("board_spec_template.latex")
    rendered = template.render(author="Maxi", specs=specs)
    return rendered


def _export_pdf(content: str, output_file: Path) -> None:
    pdf = build_pdf(content)
    pdf.save_to(output_file)
