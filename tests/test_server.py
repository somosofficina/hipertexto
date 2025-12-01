import time
from http import HTTPStatus
from threading import Thread

import httpx
import pytest

from hipertexto.main import app


def test_serve_public_folder_not_found(temp_dir, monkeypatch, capsys):
    """Test serve fails when public folder doesn't exist"""
    monkeypatch.chdir(temp_dir)

    with pytest.raises(SystemExit) as e:
        app('serve')

    assert e.value.code == 1
    stderr = capsys.readouterr().err
    assert 'public folder not found' in stderr
    assert 'ht build' in stderr


def test_serve_no_reload_starts_http_server(
    full_hipertexto_project, monkeypatch
):
    """Test that serve starts an HTTP server on the specified port"""
    monkeypatch.chdir(full_hipertexto_project)
    app('build')

    def run_server():
        app('serve --no-reload')

    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()

    # give the server time to start
    time.sleep(1)

    response = httpx.get('http://localhost:8000/', timeout=2)
    assert response.status_code == HTTPStatus.OK
    assert 'html' in response.text.lower()
