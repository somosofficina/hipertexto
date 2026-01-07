from pathlib import Path

import pytest
from rich.text import Text

from hipertexto import __version__
from hipertexto.main import app


def test_init(temp_dir, monkeypatch, capsys: pytest.CaptureFixture):
    monkeypatch.chdir(temp_dir)
    result = app('init project')

    output = Text.from_ansi(capsys.readouterr().out).plain

    assert not result
    assert 'Project project created successfully' == output


def test_init_project_already_exists(
    temp_dir, monkeypatch, capsys: pytest.CaptureFixture
):
    monkeypatch.chdir(temp_dir)

    app('init project')
    with pytest.raises(SystemExit) as e:
        app('init project')

    assert e.value.code == 1
    assert 'File project already exists' in capsys.readouterr().err


def test_build_empty_project(
    temp_dir, monkeypatch, capsys: pytest.CaptureFixture
):
    monkeypatch.chdir(temp_dir)

    app('init project')

    monkeypatch.chdir('project')
    with pytest.raises(SystemExit) as e:
        app('build')

    assert e.value.code == 1
    assert 'Content cannot be empty' in capsys.readouterr().err


@pytest.mark.parametrize(
    ('args', 'expected_output'),
    [
        ([], 'ht --help'),
        (
            ['--help'],
            'Usage',
        ),
        (['--version'], __version__),
    ],
    ids=['default', 'help', 'version'],
)
def test_main(args, expected_output, capsys: pytest.CaptureFixture):
    result = app(args)

    assert not result
    assert expected_output in capsys.readouterr().out


def test_build_sample_project_ok(
    sample_project, monkeypatch, capsys: pytest.CaptureFixture
):
    monkeypatch.chdir(sample_project)
    result = app('build')

    assert not result
    assert 'Site built successfully' in capsys.readouterr().out


def test_build_sample_project_public_structure(
    sample_project, monkeypatch, capsys: pytest.CaptureFixture
):
    monkeypatch.chdir(sample_project)
    result = app('build')

    public = Path('public')

    assert not result
    assert 'Site built successfully' in capsys.readouterr().out

    assert (public / 'index.html').exists()
    assert (public / 'inner').exists()
    assert (public / 'inner/index.html').exists()
    assert (public / 'inner/other.html').exists()


def test_build_copies_static_and_styles_content_directly(
    sample_project, monkeypatch
):
    monkeypatch.chdir(sample_project)
    app('build')

    public = Path('public')

    assert (public / 'lighthouse.jpg').exists()
    assert (public / 'style.css').exists()
    assert not (public / 'static').exists()
    assert not (public / 'styles').exists()
