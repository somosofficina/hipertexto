import cyclopts

from hipertexto import __version__
from hipertexto.console import console
from hipertexto.commands import build, init, serve

app = cyclopts.App(
    name='ht',
    help='Use ht --help to see the available commands',
    version=__version__,
    console=console,
    result_action='return_zero',
)

app.command(build)
app.command(init)
app.command(serve)

app.register_install_completion_command(
    help='Install completion for the current shell'
)
