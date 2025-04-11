"""
Test cases for the template service.
"""

import pytest
from pathlib import Path


def test_template_directory_exists(template_dir):
    """Test that the template directory exists."""
    assert template_dir.exists()
    assert template_dir.is_dir()


def test_template_file_creation(template_dir):
    """Test creating a template file."""
    template_file = template_dir / "test-template.yaml"
    template_file.write_text("""
name: "Test Template"
description: "A test template"
version: "1.0.0"
parameters: []
steps: []
""")
    assert template_file.exists()
    assert template_file.is_file()


def test_template_file_content(template_dir):
    """Test the content of a template file."""
    template_file = template_dir / "test-template.yaml"
    content = template_file.read_text()
    assert "name: \"Test Template\"" in content
    assert "version: \"1.0.0\"" in content
