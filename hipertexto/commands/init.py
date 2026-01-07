import sys
from pathlib import Path

import cyclopts
from rich.text import Text

from hipertexto.console import console, e_console
from hipertexto.styles import error, success

app = cyclopts.App()


@app.command()
def init(name: str):
    """Create a new project"""

    project_dir = Path(name)
    try:
        project_dir.mkdir()
    except FileExistsError as e:
        e_console.print(f'File {e.filename} already exists', style=error)
        sys.exit(1)

    (project_dir / 'content').mkdir()
    (project_dir / 'templates').mkdir()
    (project_dir / 'static').mkdir()
    (project_dir / 'styles').mkdir()

    styled_name = Text(name, style=success)
    console.print(f'Project {styled_name.markup} created successfully')
