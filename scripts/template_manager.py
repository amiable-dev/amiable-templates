#!/usr/bin/env python3
"""Template Manager CLI for amiable-templates.

Manages templates.yaml registry entries with schema validation.
See ADR-007 for design documentation.

Usage:
    python scripts/template_manager.py validate [--deep] [--templates PATH] [--schema PATH]
    python scripts/template_manager.py list [--format text|json] [--category CAT] [--tier TIER]
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
import jsonschema


# Default paths relative to project root
DEFAULT_TEMPLATES_PATH = Path("templates.yaml")
DEFAULT_SCHEMA_PATH = Path("templates.schema.yaml")


@dataclass
class ValidationResult:
    """Result of validation operations."""

    success: bool
    schema_errors: list[str] = field(default_factory=list)
    semantic_errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def get_yaml_handler() -> YAML:
    """Create a YAML handler configured for comment preservation."""
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
    return yaml


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file and return its contents."""
    yaml = get_yaml_handler()
    with open(path, "r") as f:
        return yaml.load(f)


def validate_schema(templates_path: Path, schema_path: Path) -> list[str]:
    """Validate templates.yaml against JSON Schema (Level 1).

    Args:
        templates_path: Path to templates.yaml
        schema_path: Path to templates.schema.yaml

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    try:
        templates_data = load_yaml(templates_path)
        schema_data = load_yaml(schema_path)
    except Exception as e:
        return [f"Failed to load YAML: {e}"]

    # Convert YAML schema to JSON Schema format
    # ruamel.yaml returns CommentedMap, convert to dict for jsonschema
    schema_dict = json.loads(json.dumps(dict(schema_data)))
    templates_dict = json.loads(json.dumps(dict(templates_data)))

    validator = jsonschema.Draft7Validator(schema_dict)
    for error in validator.iter_errors(templates_dict):
        path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
        errors.append(f"Schema error at {path}: {error.message}")

    return errors


def validate_semantic(
    templates_path: Path,
    return_warnings: bool = False
) -> list[str] | tuple[list[str], list[str]]:
    """Validate semantic constraints (Level 2).

    Checks:
    - Unique template IDs
    - Valid category references
    - Valid relates_to references
    - HTTPS URLs (warns on HTTP)

    Args:
        templates_path: Path to templates.yaml
        return_warnings: If True, return (errors, warnings) tuple

    Returns:
        List of error messages, or (errors, warnings) tuple if return_warnings=True
    """
    errors = []
    warnings = []

    try:
        data = load_yaml(templates_path)
    except Exception as e:
        errors.append(f"Failed to load YAML: {e}")
        if return_warnings:
            return errors, warnings
        return errors

    # Get category IDs
    categories = data.get("categories", [])
    category_ids = {cat["id"] for cat in categories if isinstance(cat, dict)}

    # Get templates and pre-compute all template IDs for O(n) relates_to validation
    templates = data.get("templates", [])
    all_template_ids = {t.get("id") for t in templates if isinstance(t, dict)}
    seen_ids = set()

    for i, template in enumerate(templates):
        if not isinstance(template, dict):
            errors.append(f"Template at index {i} is not a valid object")
            continue

        template_id = template.get("id", f"<unknown at index {i}>")

        # Check for duplicate IDs
        if template_id in seen_ids:
            errors.append(f"Duplicate template ID: '{template_id}'")
        seen_ids.add(template_id)

        # Check category reference
        category = template.get("category")
        if category and category not in category_ids:
            errors.append(
                f"Template '{template_id}' references non-existent category: '{category}'"
            )

        # Check relates_to references (O(1) lookup using pre-computed set)
        relates_to = template.get("relates_to", [])
        for rel in relates_to:
            if isinstance(rel, dict):
                ref_id = rel.get("template_id")
                if ref_id and ref_id not in all_template_ids:
                    errors.append(
                        f"Template '{template_id}' relates_to non-existent template: '{ref_id}'"
                    )

        # Check for HTTP URLs (should be HTTPS)
        links = template.get("links", {})
        if isinstance(links, dict):
            for link_name, url in links.items():
                if isinstance(url, str) and url.startswith("http://"):
                    warnings.append(
                        f"Template '{template_id}' has HTTP URL in {link_name}: {url} (should be HTTPS)"
                    )

    if return_warnings:
        return errors, warnings
    return errors


def validate(templates_path: Path, schema_path: Path) -> ValidationResult:
    """Run all validation levels.

    Args:
        templates_path: Path to templates.yaml
        schema_path: Path to templates.schema.yaml

    Returns:
        ValidationResult with all errors and warnings
    """
    schema_errors = validate_schema(templates_path, schema_path)
    semantic_errors, warnings = validate_semantic(templates_path, return_warnings=True)

    return ValidationResult(
        success=len(schema_errors) == 0 and len(semantic_errors) == 0,
        schema_errors=schema_errors,
        semantic_errors=semantic_errors,
        warnings=warnings,
    )


def cmd_validate(args: argparse.Namespace) -> int:
    """Handle the validate subcommand."""
    templates_path = Path(args.templates) if args.templates else DEFAULT_TEMPLATES_PATH
    schema_path = Path(args.schema) if args.schema else DEFAULT_SCHEMA_PATH

    if not templates_path.exists():
        print(f"Error: Templates file not found: {templates_path}", file=sys.stderr)
        return 1

    if not schema_path.exists():
        print(f"Error: Schema file not found: {schema_path}", file=sys.stderr)
        return 1

    # Check for --deep flag (Level 3 network validation - Phase 4)
    if args.deep:
        print("Note: --deep network validation is not yet implemented (ADR-007 Phase 4)")

    result = validate(templates_path, schema_path)

    if result.schema_errors:
        print("Schema validation errors:", file=sys.stderr)
        for error in result.schema_errors:
            print(f"  - {error}", file=sys.stderr)

    if result.semantic_errors:
        print("Semantic validation errors:", file=sys.stderr)
        for error in result.semantic_errors:
            print(f"  - {error}", file=sys.stderr)

    if result.warnings:
        print("Warnings:", file=sys.stderr)
        for warning in result.warnings:
            print(f"  - {warning}", file=sys.stderr)

    if result.success:
        print(f"Validation passed: {templates_path}")
        return 0
    else:
        print(f"Validation failed: {templates_path}", file=sys.stderr)
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """Handle the list subcommand."""
    templates_path = Path(args.templates) if hasattr(args, 'templates') and args.templates else DEFAULT_TEMPLATES_PATH

    if not templates_path.exists():
        print(f"Error: Templates file not found: {templates_path}", file=sys.stderr)
        return 1

    try:
        data = load_yaml(templates_path)
    except Exception as e:
        print(f"Error loading templates: {e}", file=sys.stderr)
        return 1

    templates = data.get("templates", [])

    # Apply filters
    if args.category:
        templates = [t for t in templates if t.get("category") == args.category]

    if args.tier:
        templates = [t for t in templates if t.get("tier") == args.tier]

    # Output format
    if args.format == "json":
        # Convert to clean dict for JSON output
        # Handle None values safely for list fields
        output = []
        for t in templates:
            output.append({
                "id": t.get("id"),
                "title": t.get("title"),
                "description": t.get("description"),
                "category": t.get("category"),
                "tier": t.get("tier"),
                "tags": list(t.get("tags") or []),
                "features": list(t.get("features") or []),
            })
        print(json.dumps(output, indent=2))
    else:
        # Text format - human readable table
        if not templates:
            print("No templates found matching criteria.")
            return 0

        # Print header
        print(f"{'ID':<30} {'Title':<35} {'Category':<20} {'Tier':<12}")
        print("-" * 97)

        for t in templates:
            template_id = t.get("id", "unknown")[:30]
            title = t.get("title", "Untitled")[:35]
            category = t.get("category", "none")[:20]
            tier = t.get("tier", "none")[:12]
            print(f"{template_id:<30} {title:<35} {category:<20} {tier:<12}")

        print(f"\nTotal: {len(templates)} template(s)")

    return 0


def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="template_manager",
        description="Manage templates.yaml registry entries with schema validation.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # validate subcommand
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate templates.yaml against schema",
    )
    validate_parser.add_argument(
        "--templates",
        help=f"Path to templates.yaml (default: {DEFAULT_TEMPLATES_PATH})",
    )
    validate_parser.add_argument(
        "--schema",
        help=f"Path to schema file (default: {DEFAULT_SCHEMA_PATH})",
    )
    validate_parser.add_argument(
        "--deep",
        action="store_true",
        help="Include network checks (URL reachability)",
    )
    validate_parser.set_defaults(func=cmd_validate)

    # list subcommand
    list_parser = subparsers.add_parser(
        "list",
        help="List templates in the registry",
    )
    list_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    list_parser.add_argument(
        "--category",
        help="Filter by category",
    )
    list_parser.add_argument(
        "--tier",
        help="Filter by tier (starter, production, stable, beta, experimental)",
    )
    list_parser.add_argument(
        "--templates",
        help=f"Path to templates.yaml (default: {DEFAULT_TEMPLATES_PATH})",
    )
    list_parser.set_defaults(func=cmd_list)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
