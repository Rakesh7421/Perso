"""
Sample test file for NewsX
"""

import pytest


def test_sample():
    """Sample test that always passes"""
    assert True


def test_newsx_exists():
    """Test that the project exists"""
    import pathlib
    project_path = pathlib.Path(__file__).parent.parent
    assert project_path.exists()
