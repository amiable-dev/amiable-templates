"""Shared fixtures for template manager tests."""

import json
import sys
import tempfile
from pathlib import Path

import pytest
from ruamel.yaml import YAML

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def yaml_handler():
    """Create a YAML handler configured for comment preservation."""
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
    return yaml


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def templates_yaml_path(project_root) -> Path:
    """Return the path to templates.yaml."""
    return project_root / "templates.yaml"


@pytest.fixture
def schema_yaml_path(project_root) -> Path:
    """Return the path to templates.schema.yaml."""
    return project_root / "templates.schema.yaml"


@pytest.fixture
def valid_templates_yaml(yaml_handler) -> str:
    """Return valid templates.yaml content as string."""
    return '''# yaml-language-server: $schema=./templates.schema.yaml
version: "1.0"

categories:
  - id: test-category
    name: "Test Category"
    icon: "material/test"
    description: "Test category for testing"

templates:
  - id: test-template
    repo:
      owner: "test-org"
      name: "test-repo"
    title: "Test Template"
    description: "A test template for validation"
    category: test-category
    tier: starter
    directories:
      docs:
        - path: "README.md"
          target: "overview.md"
          sidebar_label: "Overview"
    links:
      github: "https://github.com/test-org/test-repo"
    features:
      - "Feature 1"
      - "Feature 2"
'''


@pytest.fixture
def invalid_missing_required_field_yaml() -> str:
    """Return templates.yaml missing required fields."""
    return '''version: "1.0"

templates:
  - id: test-template
    repo:
      owner: "test-org"
      name: "test-repo"
    # Missing: title, description, category, directories
'''


@pytest.fixture
def invalid_duplicate_ids_yaml() -> str:
    """Return templates.yaml with duplicate IDs."""
    return '''version: "1.0"

categories:
  - id: test-category
    name: "Test Category"

templates:
  - id: duplicate-id
    repo:
      owner: "test-org"
      name: "test-repo"
    title: "First Template"
    description: "First template"
    category: test-category
    directories:
      docs:
        - path: "README.md"
          target: "overview.md"

  - id: duplicate-id
    repo:
      owner: "test-org"
      name: "test-repo2"
    title: "Second Template"
    description: "Second template with same ID"
    category: test-category
    directories:
      docs:
        - path: "README.md"
          target: "overview.md"
'''


@pytest.fixture
def invalid_category_reference_yaml() -> str:
    """Return templates.yaml with invalid category reference."""
    return '''version: "1.0"

categories:
  - id: existing-category
    name: "Existing Category"

templates:
  - id: test-template
    repo:
      owner: "test-org"
      name: "test-repo"
    title: "Test Template"
    description: "Template referencing non-existent category"
    category: nonexistent-category
    directories:
      docs:
        - path: "README.md"
          target: "overview.md"
'''


@pytest.fixture
def invalid_id_pattern_yaml() -> str:
    """Return templates.yaml with invalid ID pattern."""
    return '''version: "1.0"

categories:
  - id: test-category
    name: "Test Category"

templates:
  - id: Invalid_ID_With_Uppercase
    repo:
      owner: "test-org"
      name: "test-repo"
    title: "Test Template"
    description: "Template with invalid ID"
    category: test-category
    directories:
      docs:
        - path: "README.md"
          target: "overview.md"
'''


@pytest.fixture
def http_url_yaml() -> str:
    """Return templates.yaml with HTTP (not HTTPS) URL."""
    return '''version: "1.0"

categories:
  - id: test-category
    name: "Test Category"

templates:
  - id: test-template
    repo:
      owner: "test-org"
      name: "test-repo"
    title: "Test Template"
    description: "Template with HTTP URL"
    category: test-category
    directories:
      docs:
        - path: "README.md"
          target: "overview.md"
    links:
      github: "http://github.com/test-org/test-repo"
'''


@pytest.fixture
def temp_yaml_file(tmp_path):
    """Factory fixture for creating temporary YAML files."""
    def _create_temp_yaml(content: str, filename: str = "templates.yaml") -> Path:
        file_path = tmp_path / filename
        file_path.write_text(content)
        return file_path
    return _create_temp_yaml


@pytest.fixture
def temp_schema_file(tmp_path, schema_yaml_path):
    """Create a temporary copy of the schema file."""
    schema_content = schema_yaml_path.read_text()
    temp_schema = tmp_path / "templates.schema.yaml"
    temp_schema.write_text(schema_content)
    return temp_schema
