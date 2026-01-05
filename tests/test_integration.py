"""Integration tests for round-trip CRUD operations (TDD - RED phase).

These tests verify complete workflows across add, update, remove, and validate.
"""

import subprocess
import sys
from pathlib import Path

import pytest


class TestCRUDIntegration:
    """Test complete CRUD workflows."""

    def test_add_list_update_remove_roundtrip(self, project_root, tmp_path):
        """Complete CRUD cycle should work correctly."""
        from scripts.template_manager import (
            add_template,
            update_template,
            remove_template,
            load_yaml,
        )

        test_templates = tmp_path / "templates.yaml"
        test_templates.write_text('''version: "1.0"

categories:
  - id: test-category
    name: "Test Category"

templates: []
''')

        # 1. ADD
        add_result = add_template(
            templates_path=test_templates,
            template_id="crud-test",
            repo_owner="test-org",
            repo_name="test-repo",
            title="CRUD Test Template",
            description="Testing CRUD operations",
            category="test-category",
        )
        assert add_result.success is True

        # Verify add
        data = load_yaml(test_templates)
        assert len(data["templates"]) == 1
        assert data["templates"][0]["id"] == "crud-test"

        # 2. UPDATE
        update_result = update_template(
            templates_path=test_templates,
            template_id="crud-test",
            title="Updated CRUD Test",
            description="Updated description",
        )
        assert update_result.success is True

        # Verify update
        data = load_yaml(test_templates)
        assert data["templates"][0]["title"] == "Updated CRUD Test"

        # 3. REMOVE
        remove_result = remove_template(
            templates_path=test_templates,
            template_id="crud-test",
            force=True,
        )
        assert remove_result.success is True

        # Verify remove
        data = load_yaml(test_templates)
        assert len(data["templates"]) == 0

    def test_add_then_validate_passes(self, project_root, tmp_path):
        """After adding a template, validation should pass."""
        from scripts.template_manager import add_template, validate

        test_templates = tmp_path / "templates.yaml"
        test_schema = project_root / "templates.schema.yaml"

        test_templates.write_text('''version: "1.0"

categories:
  - id: test-category
    name: "Test Category"

templates: []
''')

        # Add a valid template
        add_template(
            templates_path=test_templates,
            template_id="valid-template",
            repo_owner="test-org",
            repo_name="test-repo",
            title="Valid Template",
            description="A valid test template",
            category="test-category",
        )

        # Validate should pass
        result = validate(test_templates, test_schema)
        assert result.success is True, f"Validation should pass: {result.schema_errors} {result.semantic_errors}"

    def test_multiple_operations_preserve_formatting(self, project_root, tmp_path):
        """Multiple operations should preserve YAML formatting."""
        from scripts.template_manager import add_template, update_template, remove_template

        test_templates = tmp_path / "templates.yaml"
        original_content = '''# Header comment
version: "1.0"

# Categories
categories:
  - id: test-category
    name: "Test Category"

# Templates section
templates: []
'''
        test_templates.write_text(original_content)

        # Perform multiple operations
        add_template(
            templates_path=test_templates,
            template_id="template-1",
            repo_owner="test-org",
            repo_name="repo-1",
            title="Template 1",
            description="First template",
            category="test-category",
        )

        add_template(
            templates_path=test_templates,
            template_id="template-2",
            repo_owner="test-org",
            repo_name="repo-2",
            title="Template 2",
            description="Second template",
            category="test-category",
        )

        update_template(
            templates_path=test_templates,
            template_id="template-1",
            title="Updated Template 1",
        )

        remove_template(
            templates_path=test_templates,
            template_id="template-2",
            force=True,
        )

        # Comments should still be preserved
        final_content = test_templates.read_text()
        assert "# Header comment" in final_content
        assert "# Categories" in final_content
        assert "# Templates section" in final_content

    def test_cli_add_list_validates_workflow(self, project_root, tmp_path):
        """CLI commands should work in sequence."""
        test_templates = tmp_path / "templates.yaml"
        test_templates.write_text('''version: "1.0"
categories:
  - id: test-category
    name: "Test"
templates: []
''')

        script_path = project_root / "scripts" / "template_manager.py"

        # Add via CLI
        add_result = subprocess.run(
            [
                sys.executable, str(script_path), "add",
                "--id", "cli-test",
                "--repo", "test-org/test-repo",
                "--title", "CLI Test",
                "--description", "Testing CLI",
                "--category", "test-category",
                "--templates", str(test_templates),
            ],
            capture_output=True,
            text=True,
        )
        assert add_result.returncode == 0, f"CLI add should succeed: {add_result.stderr}"

        # List via CLI
        list_result = subprocess.run(
            [
                sys.executable, str(script_path), "list",
                "--templates", str(test_templates),
            ],
            capture_output=True,
            text=True,
        )
        assert list_result.returncode == 0
        assert "cli-test" in list_result.stdout.lower()

        # Validate via CLI
        validate_result = subprocess.run(
            [
                sys.executable, str(script_path), "validate",
                "--templates", str(test_templates),
                "--schema", str(project_root / "templates.schema.yaml"),
            ],
            capture_output=True,
            text=True,
        )
        assert validate_result.returncode == 0, f"Validation should pass: {validate_result.stderr}"
