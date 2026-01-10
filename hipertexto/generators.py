import locale

import frontmatter
from jinja2 import TemplateNotFound
from markdown import markdown  # type: ignore

from hipertexto.images import copy_images_and_update_path
from hipertexto.utils import calculate_depth


def validate_frontmatter(page, file, required_keys):
    if not page.metadata:
        raise ValueError(f'Missing frontmatter of file {file}')

    missing = [key for key in required_keys if key not in page.metadata]
    if missing:
        raise ValueError(
            f'Frontmatter in {file} missing keys: {", ".join(missing)}'
        )


def get_template(env, page):
    try:
        return env.get_template(page.metadata['template'])
    except TemplateNotFound:
        raise TemplateNotFound(
            f'Template {page.metadata["template"]} not found'
        )


def render_markdown(file, directories):
    page = frontmatter.load(file)
    corrected = copy_images_and_update_path(
        directories['content'],
        directories['public'],
        file,
        directories['root'],
        page.content,
    )
    html = markdown(
        corrected,
        extensions=[
            'pymdownx.superfences',
            'pymdownx.highlight',
            'pymdownx.magiclink',
        ],
        extension_configs={
            'pymdownx.highlight': {
                'noclasses': True,
            }
        },
    )
    return page, html


def write_html(path, html):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        html,
        encoding=locale.getpreferredencoding(False),
    )


def generate_section(file, env, directories, output, pages):
    required_keys = ['title', 'template']
    section, html = render_markdown(file, directories)
    validate_frontmatter(section, file, required_keys)

    context = {
        **section.metadata,
        'content': html,
        'depth': calculate_depth(file, directories['root']),
        'url': f'{output}/',
        'pages': pages,
    }

    template = get_template(env, section)
    rendered = template.render(section=context)
    write_html(output / 'index.html', rendered)

    return context


def generate_page(file, env, directories, output):
    required_keys = ['title', 'template']
    page, html = render_markdown(file, directories)
    validate_frontmatter(page, file, required_keys)

    context = {
        **page.metadata,
        'content': html,
        'depth': calculate_depth(file, directories['root']),
        'url': file.stem,
    }

    template = get_template(env, page)
    rendered = template.render(page=context)
    write_html(output / f'{file.stem}.html', rendered)

    return context
