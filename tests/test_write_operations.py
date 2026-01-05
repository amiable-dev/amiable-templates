"""Tests for write operations: add, update, remove (TDD - RED phase).

These tests define the expected behavior for template modification commands.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


class TestAddCommand:
    """Test the add subcommand."""

    def test_add_command_exists(self, project_root):
        """add subcommand should exist."""
        result = subprocess.run(
            [sys.executable, str(project_root / "scripts" / "template_manager.py"), "add", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"add subcommand should exist: {result.stderr}"

    def test_add_creates_new_template_entry(self, project_root, tmp_path):
        """add should create a new template entry in the YAML file."""
        from scripts.template_manager import add_template, load_yaml

        # Create a test templates file
        test_templates = tmp_path / "templates.yaml"
        test_templates.write_text('''version: "1.0"

categories:
  - id: test-category
    name: "Test Category"

templates: []
''')

        # Add a new template
        result = add_template(
            templates_path=test_templates,
            template_id="new-template",
            repo_owner="test-org",
            repo_name="test-repo",
            title="New Template",
            description="A new test template",
            category="test-category",
        )

        assert result.success is True, f"Add should succeed: {result.errors}"

        # Verify the template was added
        data = load_yaml(test_templates)
        templates = data.get("templates") or []
        assert len(templates) == 1
        assert templates[0]["id"] == "new-template"

    def test_add_validates_before_writing(self, project_root, tmp_path):
        """add should validate the new template before writing."""
        from scripts.template_manager import add_template

        test_templates = tmp_path / "templates.yaml"
        test_templates.write_text('''version: "1.0"
categories: []
templates: []
''')

        # Try to add template with invalid category
        result = add_template(
            templates_path=test_templates,
            template_id="new-template",
            repo_owner="test-org",
            repo_name="test-repo",
            title="New Template",
            description="A new test template",
            category="nonexistent-category",
        )

        assert result.success is False
        assert "category" in str(result.errors).lower()

    def test_add_rejects_duplicate_id(self, project_root, tmp_path):
        """add should reject templates with duplicate IDs."""
        from scripts.template_manager import add_template

        test_templates = tmp_path / "templates.yaml"
        test_templates.write_text('''version: "1.0"

categories:
  - id: test-category
    name: "Test Category"

templates:
  - id: existing-template
    repo:
      owner: "test-org"
      name: "test-repo"
    title: "Existing Template"
    description: "Already exists"
    category: test-category
    directories:
      docs:
        - path: "README.md"
          target: "overview.md"
''')

        result = add_template(
            templates_path=test_templates,
            template_id="existing-template",
            repo_owner="test-org",
            repo_name="another-repo",
            title="Duplicate Template",
            description="Should fail",
            category="test-category",
        )

        assert result.success is False
        assert "duplicate" in str(result.errors).lower() or "exists" in str(result.errors).lower()

    def test_add_preserves_yaml_comments(self, project_root, tmp_path):
        """add should preserve existing YAML comments."""
        from scripts.template_manager import add_template

        test_templates = tmp_path / "templates.yaml"
        original_content = '''# This is a header comment
version: "1.0"

# Categories section
categories:
  - id: test-category
    name: "Test Category"

# Templates section
templates: []
'''
        test_templates.write_text(original_content)

        add_template(
            templates_path=test_templates,
            template_id="new-template",
            repo_owner="test-org",
            repo_name="test-repo",
            title="New Template",
            description="Test",
            category="test-category",
        )

        # Check that comments are preserved
        new_content = test_templates.read_text()
        assert "# This is a header comment" in new_content
        assert "# Categories section" in new_content
        assert "# Templates section" in new_content

    def test_add_validates_template_id_format(self, project_root, tmp_path):
        """add should validate template ID format (lowercase, hyphens)."""
        from scripts.template_manager import add_template

        test_templates = tmp_path / "templates.yaml"
        test_templates.write_text('''version: "1.0"
categories:
  - id: test-category
    name: "Test"
templates: []
''')

        result = add_template(
            templates_path=test_templates,
            template_id="Invalid_ID",  # Invalid: uppercase and underscore
            repo_owner="test-org",
            repo_name="test-repo",
            title="Test",
            description="Test",
            category="test-category",
        )

        assert result.success is False
        assert "id" in str(result.errors).lower() or "pattern" in str(result.errors).lower()


class TestUpdateCommand:
    """Test the update subcommand."""

    def test_update_command_exists(self, project_root):
        """update subcommand should exist."""
        result = subprocess.run(
            [sys.executable, str(project_root / "scripts" / "template_manager.py"), "update", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"update subcommand should exist: {result.stderr}"

    def test_update_modifies_existing_template(self, project_root, tmp_path):
        """update should modify an existing template's fields."""
        from scripts.template_manager import update_template, load_yaml

        test_templates = tmp_path / "templates.yaml"
        test_templates.write_text('''version: "1.0"

categories:
  - id: test-category
    name: "Test Category"

templates:
  - id: test-template
    repo:
      owner: "test-org"
      name: "test-repo"
    title: "Original Title"
    description: "Original description"
    category: test-category
    directories:
      docs:
        - path: "README.md"
          target: "overview.md"
''')

        result = update_template(
            templates_path=test_templates,
            template_id="test-template",
            title="Updated Title",
            description="Updated description",
        )

        assert result.success is True, f"Update should succeed: {result.errors}"

        data = load_yaml(test_templates)
        template = data["templates"][0]
        assert template["title"] == "Updated Title"
        assert template["description"] == "Updated description"

    def test_update_nonexistent_template_errors(self, project_root, tmp_path):
        """update should error when template doesn't exist."""
        from scripts.template_manager import update_template

        test_templates = tmp_path / "templates.yaml"
        test_templates.write_text('''version: "1.0"
categories: []
templates: []
''')

        result = update_template(
            templates_path=test_templates,
            template_id="nonexistent-template",
            title="New Title",
        )

        assert result.success is False
        assert "not found" in str(result.errors).lower() or "exist" in str(result.errors).lower()

    def test_update_validates_changes(self, project_root, tmp_path):
        """update should validate changes before writing."""
        from scripts.template_manager import update_template

        test_templates = tmp_path / "templates.yaml"
        test_templates.write_text('''version: "1.0"

categories:
  - id: test-category
    name: "Test"

templates:
  - id: test-template
    repo:
      owner: "test-org"
      name: "test-repo"
    title: "Test"
    description: "Test"
    category: test-category
    directories:
      docs:
        - path: "README.md"
          target: "overview.md"
''')

        # Try to update to invalid category
        result = update_template(
            templates_path=test_templates,
            template_id="test-template",
            category="nonexistent-category",
        )

        assert result.success is False
        assert "category" in str(result.errors).lower()

    def test_update_preserves_unmodified_fields(self, project_root, tmp_path):
        """update should preserve fields not being modified."""
        from scripts.template_manager import update_template, load_yaml

        test_templates = tmp_path / "templates.yaml"
        test_templates.write_text('''version: "1.0"

categories:
  - id: test-category
    name: "Test"

templates:
  - id: test-template
    repo:
      owner: "test-org"
      name: "test-repo"
    title: "Original Title"
    description: "Original description"
    category: test-category
    tier: starter
    tags:
      - tag1
      - tag2
    directories:
      docs:
        - path: "README.md"
          target: "overview.md"
''')

        update_template(
            templates_path=test_templates,
            template_id="test-template",
            title="Updated Title",
        )

        data = load_yaml(test_templates)
        template = data["templates"][0]
        assert template["title"] == "Updated Title"
        assert template["description"] == "Original description"  # Preserved
        assert template["tier"] == "starter"  # Preserved
        assert "tag1" in template["tags"]  # Preserved


class TestRemoveCommand:
    """Test the remove subcommand."""

    def test_remove_command_exists(self, project_root):
        """remove subcommand should exist."""
        result = subprocess.run(
            [sys.executable, str(project_root / "scripts" / "template_manager.py"), "remove", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"remove subcommand should exist: {result.stderr}"

    def test_remove_deletes_template(self, project_root, tmp_path):
        """remove should delete a template from the file."""
        from scripts.template_manager import remove_template, load_yaml

        test_templates = tmp_path / "templates.yaml"
        test_templates.write_text('''version: "1.0"

categories:
  - id: test-category
    name: "Test"

templates:
  - id: template-to-remove
    repo:
      owner: "test-org"
      name: "test-repo"
    title: "To Remove"
    description: "Will be removed"
    category: test-category
    directories:
      docs:
        - path: "README.md"
          target: "overview.md"
  - id: template-to-keep
    repo:
      owner: "test-org"
      name: "another-repo"
    title: "To Keep"
    description: "Will remain"
    category: test-category
    directories:
      docs:
        - path: "README.md"
          target: "overview.md"
''')

        result = remove_template(
            templates_path=test_templates,
            template_id="template-to-remove",
            force=True,
        )

        assert result.success is True, f"Remove should succeed: {result.errors}"

        data = load_yaml(test_templates)
        templates = data.get("templates") or []
        assert len(templates) == 1
        assert templates[0]["id"] == "template-to-keep"

    def test_remove_nonexistent_template_errors(self, project_root, tmp_path):
        """remove should error when template doesn't exist."""
        from scripts.template_manager import remove_template

        test_templates = tmp_path / "templates.yaml"
        test_templates.write_text('''version: "1.0"
categories: []
templates: []
''')

        result = remove_template(
            templates_path=test_templates,
            template_id="nonexistent-template",
            force=True,
        )

        assert result.success is False
        assert "not found" in str(result.errors).lower() or "exist" in str(result.errors).lower()

    def test_remove_checks_relates_to_references(self, project_root, tmp_path):
        """remove should warn/error if other templates reference it."""
        from scripts.template_manager import remove_template

        test_templates = tmp_path / "templates.yaml"
        test_templates.write_text('''version: "1.0"

categories:
  - id: test-category
    name: "Test"

templates:
  - id: referenced-template
    repo:
      owner: "test-org"
      name: "test-repo"
    title: "Referenced"
    description: "Other templates reference this"
    category: test-category
    directories:
      docs:
        - path: "README.md"
          target: "overview.md"
  - id: referencing-template
    repo:
      owner: "test-org"
      name: "another-repo"
    title: "Referencing"
    description: "References another template"
    category: test-category
    directories:
      docs:
        - path: "README.md"
          target: "overview.md"
    relates_to:
      - template_id: referenced-template
        relationship: production_version
''')

        result = remove_template(
            templates_path=test_templates,
            template_id="referenced-template",
            force=False,
        )

        # Should fail or warn about the reference
        assert result.success is False or len(result.warnings) > 0
