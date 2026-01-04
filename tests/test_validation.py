"""Tests for template validation logic (TDD - RED phase).

These tests define the expected behavior for Level 1 (Schema) and Level 2 (Semantic) validation.
"""

import pytest


class TestLevel1SchemaValidation:
    """Test JSON Schema validation (Level 1)."""

    def test_validate_schema_valid_templates_returns_no_errors(
        self, temp_yaml_file, temp_schema_file, valid_templates_yaml
    ):
        """Valid templates.yaml should pass schema validation."""
        from scripts.template_manager import validate_schema

        templates_path = temp_yaml_file(valid_templates_yaml)
        errors = validate_schema(templates_path, temp_schema_file)
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_validate_schema_missing_required_field_returns_error(
        self, temp_yaml_file, temp_schema_file, invalid_missing_required_field_yaml
    ):
        """Missing required fields should return validation errors."""
        from scripts.template_manager import validate_schema

        templates_path = temp_yaml_file(invalid_missing_required_field_yaml)
        errors = validate_schema(templates_path, temp_schema_file)
        assert len(errors) > 0, "Expected validation errors for missing required fields"
        # Should mention the missing field
        error_text = str(errors)
        assert any(
            field in error_text.lower()
            for field in ["title", "description", "category", "directories"]
        ), f"Error should mention missing field, got: {errors}"

    def test_validate_schema_invalid_template_id_pattern_returns_error(
        self, temp_yaml_file, temp_schema_file, invalid_id_pattern_yaml
    ):
        """Template IDs not matching pattern should return validation errors."""
        from scripts.template_manager import validate_schema

        templates_path = temp_yaml_file(invalid_id_pattern_yaml)
        errors = validate_schema(templates_path, temp_schema_file)
        assert len(errors) > 0, "Expected validation errors for invalid ID pattern"

    def test_validate_schema_invalid_type_returns_error(
        self, temp_yaml_file, temp_schema_file
    ):
        """Invalid types should return validation errors."""
        from scripts.template_manager import validate_schema

        invalid_yaml = '''version: "1.0"
templates:
  - id: "test"
    repo:
      owner: "test-org"
      name: "test-repo"
    title: 123  # Should be string
    description: "Test"
    category: "test"
    directories:
      docs:
        - path: "README.md"
          target: "overview.md"
'''
        templates_path = temp_yaml_file(invalid_yaml)
        errors = validate_schema(templates_path, temp_schema_file)
        assert len(errors) > 0, "Expected validation errors for invalid type"


class TestLevel2SemanticValidation:
    """Test semantic validation (Level 2)."""

    def test_validate_semantic_duplicate_ids_returns_error(
        self, temp_yaml_file, invalid_duplicate_ids_yaml
    ):
        """Duplicate template IDs should return validation errors."""
        from scripts.template_manager import validate_semantic

        templates_path = temp_yaml_file(invalid_duplicate_ids_yaml)
        errors = validate_semantic(templates_path)
        assert len(errors) > 0, "Expected validation errors for duplicate IDs"
        assert "duplicate" in str(errors).lower(), f"Error should mention duplicate, got: {errors}"

    def test_validate_semantic_invalid_category_reference_returns_error(
        self, temp_yaml_file, invalid_category_reference_yaml
    ):
        """Invalid category references should return validation errors."""
        from scripts.template_manager import validate_semantic

        templates_path = temp_yaml_file(invalid_category_reference_yaml)
        errors = validate_semantic(templates_path)
        assert len(errors) > 0, "Expected validation errors for invalid category reference"
        assert "category" in str(errors).lower(), f"Error should mention category, got: {errors}"

    def test_validate_semantic_http_url_returns_warning(
        self, temp_yaml_file, http_url_yaml
    ):
        """HTTP (not HTTPS) URLs should return warnings."""
        from scripts.template_manager import validate_semantic

        templates_path = temp_yaml_file(http_url_yaml)
        errors, warnings = validate_semantic(templates_path, return_warnings=True)
        assert len(warnings) > 0, "Expected warnings for HTTP URL"
        assert "http" in str(warnings).lower(), f"Warning should mention HTTP, got: {warnings}"

    def test_validate_semantic_valid_templates_returns_no_errors(
        self, temp_yaml_file, valid_templates_yaml
    ):
        """Valid templates should pass semantic validation."""
        from scripts.template_manager import validate_semantic

        templates_path = temp_yaml_file(valid_templates_yaml)
        errors = validate_semantic(templates_path)
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_validate_semantic_invalid_relates_to_reference(self, temp_yaml_file):
        """relates_to referencing non-existent template should return error."""
        from scripts.template_manager import validate_semantic

        invalid_yaml = '''version: "1.0"
categories:
  - id: test-category
    name: "Test Category"

templates:
  - id: test-template
    repo:
      owner: "test-org"
      name: "test-repo"
    title: "Test Template"
    description: "Template with invalid relates_to"
    category: test-category
    directories:
      docs:
        - path: "README.md"
          target: "overview.md"
    relates_to:
      - template_id: nonexistent-template
        relationship: production_version
'''
        templates_path = temp_yaml_file(invalid_yaml)
        errors = validate_semantic(templates_path)
        assert len(errors) > 0, "Expected validation errors for invalid relates_to reference"


class TestCombinedValidation:
    """Test combined validation (Level 1 + Level 2)."""

    def test_validate_runs_both_schema_and_semantic(
        self, temp_yaml_file, temp_schema_file, valid_templates_yaml
    ):
        """validate() should run both schema and semantic validation."""
        from scripts.template_manager import validate

        templates_path = temp_yaml_file(valid_templates_yaml)
        result = validate(templates_path, temp_schema_file)
        assert result.success is True
        assert result.schema_errors == []
        assert result.semantic_errors == []

    def test_validate_returns_all_errors(self, temp_yaml_file, temp_schema_file):
        """validate() should return both schema and semantic errors."""
        from scripts.template_manager import validate

        # This YAML has both schema and semantic issues
        invalid_yaml = '''version: "1.0"
categories:
  - id: existing-category
    name: "Existing"

templates:
  - id: template-1
    repo:
      owner: "test"
      name: "test"
    title: "Template 1"
    description: "Test"
    category: nonexistent-category  # semantic error
    directories:
      docs:
        - path: "README.md"
          target: "overview.md"
'''
        templates_path = temp_yaml_file(invalid_yaml)
        result = validate(templates_path, temp_schema_file)
        assert result.success is False
        # Should have semantic error for category reference
        assert len(result.semantic_errors) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_validate_empty_file_returns_error(self, temp_yaml_file, temp_schema_file):
        """Empty YAML file should return validation error, not crash."""
        from scripts.template_manager import validate

        empty_path = temp_yaml_file("")
        result = validate(empty_path, temp_schema_file)
        assert result.success is False
        assert len(result.schema_errors) > 0

    def test_validate_list_root_returns_error(self, temp_yaml_file, temp_schema_file):
        """YAML with list at root should return validation error, not crash."""
        from scripts.template_manager import validate

        list_yaml = '''- item1
- item2
- item3
'''
        templates_path = temp_yaml_file(list_yaml)
        result = validate(templates_path, temp_schema_file)
        assert result.success is False
        assert len(result.schema_errors) > 0
        assert "dictionary" in str(result.schema_errors).lower() or "dict" in str(result.schema_errors).lower()

    def test_validate_explicit_null_values_no_crash(self, temp_yaml_file, temp_schema_file):
        """Explicit null values (categories: null) should not crash."""
        from scripts.template_manager import validate

        null_yaml = '''version: "1.0"
categories: null
templates: null
'''
        templates_path = temp_yaml_file(null_yaml)
        result = validate(templates_path, temp_schema_file)
        # Should not crash - may pass or fail validation, but shouldn't raise exception
        assert isinstance(result.success, bool)

    def test_validate_semantic_handles_missing_category_id(self, temp_yaml_file):
        """Categories without 'id' field should not crash."""
        from scripts.template_manager import validate_semantic

        invalid_yaml = '''version: "1.0"
categories:
  - name: "Missing ID Category"

templates:
  - id: test-template
    repo:
      owner: "test"
      name: "test"
    title: "Test"
    description: "Test"
    category: test-category
    directories:
      docs:
        - path: "README.md"
          target: "overview.md"
'''
        templates_path = temp_yaml_file(invalid_yaml)
        # Should not crash
        errors = validate_semantic(templates_path)
        assert isinstance(errors, list)


class TestValidateWithRealFiles:
    """Test validation against actual project files."""

    def test_validate_current_templates_yaml_passes(
        self, templates_yaml_path, schema_yaml_path
    ):
        """Current templates.yaml in project should pass all validation."""
        from scripts.template_manager import validate

        result = validate(templates_yaml_path, schema_yaml_path)
        assert result.success is True, (
            f"Current templates.yaml should be valid.\n"
            f"Schema errors: {result.schema_errors}\n"
            f"Semantic errors: {result.semantic_errors}"
        )
