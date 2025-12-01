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
