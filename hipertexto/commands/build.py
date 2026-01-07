import shutil
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from cyclopts import App

from hipertexto.jinja_globals import rel_path
from hipertexto.process_md import process_markdown
from hipertexto.styles import error, success


app = App()

console = Console()
e_console = Console(stderr=True)


def sort_by_key(page_metadata, key='title'):
    return page_metadata[key]


@app.command()
def build():
    """Build your site to the public folder"""

    root_path = Path('.')
    directories = {
        'root': root_path,
        'contents': root_path / 'content',
        'styles': root_path / 'styles',
        'static': root_path / 'static',
        'templates': root_path / 'templates',
        'public': Path('public'),
    }

    directories['public'].mkdir(exist_ok=True)

    # content and templates must exist and not be empty
    content_is_empty = not directories['contents'].exists() or not any(
        directories['contents'].iterdir()
    )
    template_is_empty = not directories['templates'].exists() or not any(
        directories['templates'].iterdir()
    )
    if content_is_empty or template_is_empty:
        e_console.print(
            'Content and Templates directories cannot be empty',
            style=error,
        )
        sys.exit(1)

    # Styles and Static content should be on public
    for dir_path in {
        directories['styles'],
        directories['static'],
    }:
        if not dir_path.is_dir():
            continue

        for item in dir_path.iterdir():
            dest_path = directories['public'] / item.name
            if item.is_dir():
                shutil.copytree(item, dest_path, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest_path)

    env = Environment(loader=FileSystemLoader(directories['templates']))
    env.globals['rel_path'] = rel_path

    try:
        for item in directories['contents'].iterdir():
            if item.is_dir():
                index_file = item / '_index.md'
                section_dir = directories['public'] / item.name
                section_dir.mkdir(parents=True, exist_ok=True)
                section_pages = []

                for file in item.glob('*.md'):
                    if file != index_file:
                        page_context = process_markdown(
                            file=file,
                            jinja_env=env,
                            content_dir=directories['contents'],
                            public_dir=directories['public'],
                            root_dir=directories['root'],
                            section_dir=section_dir,
                        )
                        section_pages.append(page_context)

                if index_file.exists():
                    section_pages.sort(key=sort_by_key, reverse=True)
                    process_markdown(
                        file=index_file,
                        jinja_env=env,
                        content_dir=directories['contents'],
                        public_dir=directories['public'],
                        root_dir=directories['root'],
                        section_dir=section_dir,
                        section_pages=section_pages,
                    )

            elif item.suffix == '.md':
                process_markdown(
                    file=item,
                    jinja_env=env,
                    content_dir=directories['contents'],
                    public_dir=directories['public'],
                    root_dir=directories['root'],
                )

        console.print('Site built successfully', style=success)

    except Exception as e:
        e_console.print(f'Error: {e}', style=error)
        sys.exit(1)
