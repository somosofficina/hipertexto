import shutil
import sys
from pathlib import Path

from cyclopts import App
from jinja2 import Environment, FileSystemLoader

from hipertexto.console import console, e_console
from hipertexto.generators import generate_page, generate_section
from hipertexto.jinja_globals import rel_path
from hipertexto.styles import error, success

app = App()


def sort_by_key(page_metadata, key='title'):
    return page_metadata[key]


def delete_and_recreate_path(path):
    if path.exists():
        shutil.rmtree(path)

    path.mkdir()


def ensure_not_empty(path, pathname):
    """Check if a folder exists and it's not empty"""
    exists = path.exists()
    has_content = any(path.iterdir())

    if not exists or not has_content:
        error_message = f'{pathname} cannot be empty'
        e_console.print(error_message, style=error)
        sys.exit(1)


def move_folder_to_public(path, public):
    for item in path.iterdir():
        destination = public / item.name
        if item.is_dir():
            shutil.copytree(item, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(item, destination)


def process_entries(source, output, directories, env):
    """Recursive process content entries"""
    output.mkdir(parents=True, exist_ok=True)
    index = source / '_index.md'
    pages = []

    for entry in source.iterdir():
        if entry.is_dir():
            process_entries(
                source=entry,
                output=output / entry.name,
                directories=directories,
                env=env
            )
        elif entry.suffix == '.md' and entry != index:
            pages.append(generate_page(entry, env, directories, output))

    if index.exists():
        pages.sort(key=sort_by_key, reverse=True)
        generate_section(index, env, directories, output, pages)


@app.command()
def build():
    """Build your site to the public folder"""

    root_path = Path('.')
    directories = {
        'root': root_path,
        'content': root_path / 'content',
        'styles': root_path / 'styles',
        'static': root_path / 'static',
        'templates': root_path / 'templates',
        'public': Path('public'),
    }

    # ensure that public is cleared before build
    delete_and_recreate_path(directories['public'])

    # content and templates must exist and not be empty
    ensure_not_empty(directories['content'], 'Content')
    ensure_not_empty(directories['templates'], 'Templates')

    # styles and static content should be on public
    move_folder_to_public(directories['styles'], directories['public'])
    move_folder_to_public(directories['static'], directories['public'])

    # load jinja environment
    env = Environment(loader=FileSystemLoader(directories['templates']))
    env.globals['rel_path'] = rel_path

    try:
        process_entries(
            source=directories['content'],
            output=directories['public'],
            env=env,
            directories=directories
        )
        console.print('Site built successfully', style=success)
    except Exception as exc:
        e_console.print(f'Error: {exc}', style=error)
        sys.exit(1)
