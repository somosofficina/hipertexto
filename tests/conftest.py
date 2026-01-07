import shutil
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    temp_dir = Path('temp_test_dir')
    temp_dir.mkdir(exist_ok=True)
    yield temp_dir

    # removing the temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_project(temp_dir):
    asset = 'tests/assets/sample_project'
    shutil.copytree(asset, temp_dir, dirs_exist_ok=True)

    return temp_dir


@pytest.fixture
def sample_project_with_public(temp_dir):
    asset = 'tests/assets/sample_project_with_public'
    shutil.copytree(asset, temp_dir, dirs_exist_ok=True)

    return temp_dir
