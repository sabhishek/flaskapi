from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import Dict

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"

env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


def render(resource_type: str, context: Dict) -> str:
    template_file = f"{resource_type}.yaml.j2"
    template = env.get_template(template_file)
    return template.render(**context)
