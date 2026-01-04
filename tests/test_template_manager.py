"""Tests for template_manager.py CLI (TDD - RED phase).

These tests define the expected CLI behavior for the template manager.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


class TestCLIStructure:
    """Test CLI structure and subcommands."""

    def test_cli_has_validate_subcommand(self, project_root):
        """CLI should have a validate subcommand."""
        result = subprocess.run(
            [sys.executable, str(project_root / "scripts" / "template_manager.py"), "validate", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"validate subcommand should exist: {result.stderr}"
        assert "validate" in result.stdout.lower()

    def test_cli_has_list_subcommand(self, project_root):
        """CLI should have a list subcommand."""
        result = subprocess.run(
            [sys.executable, str(project_root / "scripts" / "template_manager.py"), "list", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"list subcommand should exist: {result.stderr}"
        assert "list" in result.stdout.lower()

    def test_cli_help_shows_available_commands(self, project_root):
        """CLI help should show available subcommands."""
        result = subprocess.run(
            [sys.executable, str(project_root / "scripts" / "template_manager.py"), "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "validate" in result.stdout.lower()
        assert "list" in result.stdout.lower()

    def test_cli_invalid_command_shows_error(self, project_root):
        """CLI should show error for invalid subcommand."""
        result = subprocess.run(
            [sys.executable, str(project_root / "scripts" / "template_manager.py"), "invalid-command"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

    def test_cli_no_command_shows_help(self, project_root):
        """CLI with no command should show help or error."""
        result = subprocess.run(
            [sys.executable, str(project_root / "scripts" / "template_manager.py")],
            capture_output=True,
            text=True,
        )
        # Should either show help (return 0) or error (return non-0)
        # Either way, help info should be present
        combined_output = result.stdout + result.stderr
        assert "validate" in combined_output.lower() or "usage" in combined_output.lower()


class TestValidateCommand:
    """Test the validate subcommand."""

    def test_validate_command_succeeds_on_valid_templates(self, project_root):
        """validate command should succeed on valid templates.yaml."""
        result = subprocess.run(
            [sys.executable, str(project_root / "scripts" / "template_manager.py"), "validate"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        assert result.returncode == 0, f"validate should succeed: {result.stderr}"

    def test_validate_command_fails_on_invalid_file(self, project_root, tmp_path):
        """validate command should fail on invalid file."""
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text("invalid: yaml: content")

        result = subprocess.run(
            [
                sys.executable,
                str(project_root / "scripts" / "template_manager.py"),
                "validate",
                "--templates",
                str(invalid_yaml),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

    def test_validate_command_accepts_custom_paths(self, project_root, tmp_path, valid_templates_yaml):
        """validate command should accept custom template and schema paths."""
        templates_file = tmp_path / "templates.yaml"
        templates_file.write_text(valid_templates_yaml)

        result = subprocess.run(
            [
                sys.executable,
                str(project_root / "scripts" / "template_manager.py"),
                "validate",
                "--templates",
                str(templates_file),
                "--schema",
                str(project_root / "templates.schema.yaml"),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"validate should succeed with custom paths: {result.stderr}"

    def test_validate_command_outputs_errors_clearly(self, project_root, tmp_path):
        """validate command should output errors in a clear format."""
        invalid_yaml = tmp_path / "templates.yaml"
        invalid_yaml.write_text('''version: "1.0"
templates:
  - id: test
    # Missing required fields
''')
        result = subprocess.run(
            [
                sys.executable,
                str(project_root / "scripts" / "template_manager.py"),
                "validate",
                "--templates",
                str(invalid_yaml),
                "--schema",
                str(project_root / "templates.schema.yaml"),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        # Output should contain error information
        combined = result.stdout + result.stderr
        assert "error" in combined.lower() or "failed" in combined.lower()


class TestListCommand:
    """Test the list subcommand."""

    def test_list_command_outputs_templates(self, project_root):
        """list command should output template information."""
        result = subprocess.run(
            [sys.executable, str(project_root / "scripts" / "template_manager.py"), "list"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        assert result.returncode == 0, f"list should succeed: {result.stderr}"
        # Should contain at least one known template
        assert "litellm" in result.stdout.lower() or "langfuse" in result.stdout.lower()

    def test_list_command_json_format_is_valid_json(self, project_root):
        """list --format json should output valid JSON."""
        result = subprocess.run(
            [
                sys.executable,
                str(project_root / "scripts" / "template_manager.py"),
                "list",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        assert result.returncode == 0, f"list --format json should succeed: {result.stderr}"
        # Should be valid JSON
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            pytest.fail(f"Output should be valid JSON: {e}\nOutput: {result.stdout}")
        assert isinstance(data, list), "JSON output should be a list of templates"
        assert len(data) > 0, "Should have at least one template"

    def test_list_command_filter_by_category(self, project_root):
        """list --category should filter templates by category."""
        result = subprocess.run(
            [
                sys.executable,
                str(project_root / "scripts" / "template_manager.py"),
                "list",
                "--category",
                "observability",
            ],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        assert result.returncode == 0
        # Should contain observability templates
        assert "litellm" in result.stdout.lower()

    def test_list_command_filter_by_tier(self, project_root):
        """list --tier should filter templates by tier."""
        result = subprocess.run(
            [
                sys.executable,
                str(project_root / "scripts" / "template_manager.py"),
                "list",
                "--tier",
                "starter",
            ],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        assert result.returncode == 0
        # Should contain starter tier templates
        assert "starter" in result.stdout.lower()

    def test_list_command_nonexistent_category_shows_empty_or_message(self, project_root):
        """list --category with nonexistent category should handle gracefully."""
        result = subprocess.run(
            [
                sys.executable,
                str(project_root / "scripts" / "template_manager.py"),
                "list",
                "--category",
                "nonexistent-category-xyz",
            ],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        # Should either succeed with empty result or show appropriate message
        # Not fail catastrophically
        assert result.returncode == 0

    def test_list_json_contains_expected_fields(self, project_root):
        """JSON output should contain expected template fields."""
        result = subprocess.run(
            [
                sys.executable,
                str(project_root / "scripts" / "template_manager.py"),
                "list",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) > 0

        # Check first template has expected fields
        template = data[0]
        expected_fields = ["id", "title", "description", "category", "tier"]
        for field in expected_fields:
            assert field in template, f"Template should have '{field}' field"
