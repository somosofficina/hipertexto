import os
import sys
from http.server import HTTPServer
from threading import Thread

import cyclopts
from rich.text import Text
from watchfiles import watch

from hipertexto.commands import build
from hipertexto.console import console, e_console
from hipertexto.local_server import CleanURLHandler
from hipertexto.styles import error, success, warning

app = cyclopts.App()


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
