import os
import sys
from http.server import HTTPServer
from pathlib import Path
from threading import Thread
from typing import Final

import cyclopts
from rich.console import Console
from rich.text import Text
from watchfiles import watch

from hipertexto import __version__
from hipertexto.local_server import CleanURLHandler
from hipertexto.commands import build

from .styles import error, success, warning

console = Console()
e_console = Console(stderr=True)
app = cyclopts.App(
    name='ht',
    help='Use ht --help to see the available commands',
    version=__version__,
    console=console,
    result_action='return_zero',
)

app.command(build)
app.register_install_completion_command(
    help='Install completion for the current shell'
)

CURRENT_SCRIPT_PATH: Final[Path] = Path(__file__).resolve()
TEMPLATES_DIR: Final[Path] = CURRENT_SCRIPT_PATH.parent / 'templates'


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


def watch_and_rebuild():
    console.print('Watching for file changes...', style=success)
    for changes in watch(
        '../content', '../templates', '../static', '../styles'
    ):
        console.print(
            f'Detected changes in {len(changes)} file(s), rebuilding...',
            style=warning,
        )
        os.chdir('..')  # change to project folder before build
        build()
        os.chdir('public')  # go back to public folder so we keep serving
        console.print('Rebuild complete!', style=success)


@app.command()
def serve(port: int = 8000, reload: bool = True):
    """Run a http server from public folder in local network"""
    try:
        os.chdir('public')
    except FileNotFoundError:
        e_console.print('public folder not found', style=error)
        hipertexto_build = Text('ht build', style=success)
        e_console.print(
            f'Run {hipertexto_build.markup} before running "ht serve" again'
        )
        sys.exit(1)

    if reload:
        watcher_thread = Thread(target=watch_and_rebuild, daemon=True)
        watcher_thread.start()

    with HTTPServer(('', port), CleanURLHandler) as httpd:
        console.print(
            f'Serving at [link=http://0.0.0.0:{port}]http://0.0.0.0:{port}[/link]',
            style=success,
        )
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.shutdown()
            console.print('\nLocal server stopped.', style=warning)
