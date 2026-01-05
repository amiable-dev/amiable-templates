#!/usr/bin/env python3
"""Template Manager CLI for amiable-templates.

Manages templates.yaml registry entries with schema validation.
See ADR-007 for design documentation.

Usage:
    python scripts/template_manager.py validate [--deep] [--templates PATH] [--schema PATH]
    python scripts/template_manager.py list [--format text|json] [--category CAT] [--tier TIER]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
import jsonschema


class SafeJSONEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime and other special types from ruamel.yaml."""

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


# Default paths relative to project root (script is in scripts/)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DEFAULT_TEMPLATES_PATH = PROJECT_ROOT / "templates.yaml"
DEFAULT_SCHEMA_PATH = PROJECT_ROOT / "templates.schema.yaml"


@dataclass
class ValidationResult:
    """Result of validation operations."""

    success: bool
    schema_errors: list[str] = field(default_factory=list)
    semantic_errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class WriteResult:
    """Result of write operations (add, update, remove)."""

    success: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# Template ID pattern: lowercase letters, numbers, hyphens, must start with letter
TEMPLATE_ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")

# GitHub owner/repo patterns (security: prevent injection via malformed names)
# Owner: alphanumeric and hyphens, 1-39 chars, cannot start/end with hyphen
GITHUB_OWNER_PATTERN = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$")
# Repo: alphanumeric, hyphens, underscores, dots, 1-100 chars
GITHUB_REPO_PATTERN = re.compile(r"^[a-zA-Z0-9._-]{1,100}$")


def get_yaml_handler() -> YAML:
    """Create a YAML handler configured for comment preservation."""
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
    return yaml


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file and return its contents.

    Returns empty dict if file is empty or contains no data.
    Raises ValueError if root is not a dictionary.
    Raises ValueError if path is a symlink (security: prevent LFI attacks).

    Uses O_NOFOLLOW to prevent TOCTOU race conditions with symlinks.
    """
    import os
    import errno

    yaml = get_yaml_handler()

    # Security: Use O_NOFOLLOW to atomically reject symlinks (prevents TOCTOU)
    # This is safer than checking is_symlink() then open() - no race window
    try:
        fd = os.open(str(path), os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as e:
        if e.errno == errno.ELOOP:
            raise ValueError(f"Refusing to read symlink for security: {path}")
        raise

    try:
        with os.fdopen(fd, "r") as f:
            data = yaml.load(f)
            # Handle empty files that return None
            if data is None:
                return {}
            # Ensure root is a dictionary
            if not isinstance(data, dict):
                raise ValueError(f"YAML root must be a dictionary, got {type(data).__name__}")
            return data
    except Exception:
        # fdopen takes ownership of fd on success, but if yaml.load fails we need cleanup
        # Note: fdopen closes fd on success, so we only need to handle exceptions
        raise


def load_yaml_raw(path: Path):
    """Load YAML preserving ruamel.yaml structure for comment preservation.

    Returns the raw ruamel.yaml CommentedMap for modification.
    Raises ValueError if path is a symlink (security: prevent LFI attacks).

    Uses O_NOFOLLOW to prevent TOCTOU race conditions with symlinks.
    """
    import os
    import errno

    yaml = get_yaml_handler()

    # Security: Use O_NOFOLLOW to atomically reject symlinks (prevents TOCTOU)
    try:
        fd = os.open(str(path), os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as e:
        if e.errno == errno.ELOOP:
            raise ValueError(f"Refusing to read symlink for security: {path}")
        raise

    with os.fdopen(fd, "r") as f:
        return yaml.load(f)


def save_yaml(path: Path, data) -> None:
    """Save YAML data preserving comments and formatting.

    Uses secure temporary file to prevent symlink attacks.
    Preserves original file permissions if the file exists.
    Uses O_NOFOLLOW for atomic symlink rejection (no TOCTOU race).

    Args:
        path: Path to write to
        data: ruamel.yaml CommentedMap or dict to save
    """
    import tempfile
    import os
    import stat
    import errno

    yaml = get_yaml_handler()

    # Get original file permissions atomically using O_NOFOLLOW to prevent TOCTOU
    # O_NOFOLLOW ensures we don't follow symlinks - raises ELOOP if symlink
    original_mode = None
    if path.exists():
        try:
            # Open without following symlinks and get mode from fd (atomic)
            check_fd = os.open(str(path), os.O_RDONLY | os.O_NOFOLLOW)
            try:
                original_mode = stat.S_IMODE(os.fstat(check_fd).st_mode)
            finally:
                os.close(check_fd)
        except OSError as e:
            if e.errno == errno.ELOOP:
                raise ValueError(f"Refusing to write to symlink for security: {path}")
            # For other errors (permission denied, etc.), use default mode
            original_mode = None

    # Use secure temp file in same directory for atomic rename
    dir_path = path.parent
    fd, temp_path = tempfile.mkstemp(suffix=".yaml.tmp", dir=dir_path)
    try:
        with os.fdopen(fd, "w") as f:
            yaml.dump(data, f)

        # Restore original permissions or use sensible default (0644)
        if original_mode is not None:
            os.chmod(temp_path, original_mode)
        else:
            os.chmod(temp_path, 0o644)

        # Atomic move (works on same filesystem)
        Path(temp_path).replace(path)
    except Exception:
        # Clean up temp file on error
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise


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
    # Use SafeJSONEncoder to handle datetime objects
    schema_dict = json.loads(json.dumps(dict(schema_data), cls=SafeJSONEncoder))
    templates_dict = json.loads(json.dumps(dict(templates_data), cls=SafeJSONEncoder))

    # Create validator with disabled $ref resolution to prevent SSRF
    # Using a resolver that refuses to resolve remote references
    from jsonschema import RefResolver

    class NoRemoteRefResolver(RefResolver):
        """Resolver that refuses to fetch remote references (SSRF prevention)."""

        def resolve_remote(self, uri):
            raise jsonschema.RefResolutionError(
                f"Remote $ref resolution disabled for security: {uri}"
            )

    resolver = NoRemoteRefResolver.from_schema(schema_dict)
    validator = jsonschema.Draft7Validator(schema_dict, resolver=resolver)
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

    # Get category IDs (safely handle categories without 'id' field or explicit null)
    categories = data.get("categories") or []
    category_ids = {cat.get("id") for cat in categories if isinstance(cat, dict) and cat.get("id")}

    # Get templates and pre-compute all template IDs for O(n) relates_to validation
    # Use 'or []' to handle explicit null values (e.g., templates: null)
    templates = data.get("templates") or []
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
        # Use 'or []' to handle explicit null values
        relates_to = template.get("relates_to") or []
        for idx, rel in enumerate(relates_to):
            if not isinstance(rel, dict):
                errors.append(
                    f"Template '{template_id}' has invalid relates_to entry at index {idx}: expected dict, got {type(rel).__name__}"
                )
                continue
            ref_id = rel.get("template_id")
            if ref_id and ref_id not in all_template_ids:
                errors.append(
                    f"Template '{template_id}' relates_to non-existent template: '{ref_id}'"
                )

        # Check for HTTP URLs (should be HTTPS)
        # Use 'or {}' to handle explicit null values
        links = template.get("links") or {}
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


def add_template(
    templates_path: Path,
    template_id: str,
    repo_owner: str,
    repo_name: str,
    title: str,
    description: str,
    category: str,
    tier: str = "starter",
    tags: list[str] | None = None,
    features: list[str] | None = None,
) -> WriteResult:
    """Add a new template to the registry.

    Args:
        templates_path: Path to templates.yaml
        template_id: Unique template identifier
        repo_owner: GitHub repository owner
        repo_name: GitHub repository name
        title: Display title
        description: Brief description
        category: Category ID reference
        tier: Template tier (starter, production, stable, beta, experimental)
        tags: Optional list of tags
        features: Optional list of features

    Returns:
        WriteResult indicating success or failure
    """
    errors = []
    warnings = []

    # Validate template ID format
    if not TEMPLATE_ID_PATTERN.match(template_id):
        errors.append(
            f"Invalid template ID '{template_id}': must be lowercase letters, numbers, "
            "and hyphens, starting with a letter"
        )
        return WriteResult(success=False, errors=errors)

    # Validate repo_owner (security: prevent injection)
    if not GITHUB_OWNER_PATTERN.match(repo_owner):
        errors.append(
            f"Invalid repo owner '{repo_owner}': must be 1-39 alphanumeric characters or hyphens, "
            "cannot start or end with hyphen"
        )
        return WriteResult(success=False, errors=errors)

    # Validate repo_name (security: prevent injection)
    if not GITHUB_REPO_PATTERN.match(repo_name):
        errors.append(
            f"Invalid repo name '{repo_name}': must be 1-100 alphanumeric characters, hyphens, "
            "underscores, or dots"
        )
        return WriteResult(success=False, errors=errors)

    try:
        data = load_yaml_raw(templates_path)
    except Exception as e:
        return WriteResult(success=False, errors=[f"Failed to load YAML: {e}"])

    # Handle None data
    if data is None:
        data = {}

    # Get existing templates and categories
    templates = data.get("templates") or []
    categories = data.get("categories") or []

    # Check for duplicate ID
    existing_ids = {t.get("id") for t in templates if isinstance(t, dict)}
    if template_id in existing_ids:
        errors.append(f"Template with ID '{template_id}' already exists")
        return WriteResult(success=False, errors=errors)

    # Check category exists
    category_ids = {c.get("id") for c in categories if isinstance(c, dict)}
    if category not in category_ids:
        errors.append(f"Category '{category}' does not exist")
        return WriteResult(success=False, errors=errors)

    # Build new template entry
    from ruamel.yaml.comments import CommentedMap, CommentedSeq

    new_template = CommentedMap()
    new_template["id"] = template_id
    new_template["repo"] = CommentedMap([("owner", repo_owner), ("name", repo_name)])
    new_template["title"] = title
    new_template["description"] = description
    new_template["category"] = category
    new_template["tier"] = tier

    # Add directories with minimal required structure
    docs_entry = CommentedMap([("path", "README.md"), ("target", "overview.md")])
    new_template["directories"] = CommentedMap([("docs", CommentedSeq([docs_entry]))])

    if tags:
        new_template["tags"] = CommentedSeq(tags)
    if features:
        new_template["features"] = CommentedSeq(features)

    # Add links
    new_template["links"] = CommentedMap([
        ("github", f"https://github.com/{repo_owner}/{repo_name}")
    ])

    # Append to templates list
    if not isinstance(templates, list):
        templates = []
    templates.append(new_template)
    data["templates"] = templates

    # Save
    try:
        save_yaml(templates_path, data)
    except Exception as e:
        return WriteResult(success=False, errors=[f"Failed to save YAML: {e}"])

    return WriteResult(success=True, warnings=warnings)


def update_template(
    templates_path: Path,
    template_id: str,
    title: str | None = None,
    description: str | None = None,
    category: str | None = None,
    tier: str | None = None,
    tags: list[str] | None = None,
    features: list[str] | None = None,
) -> WriteResult:
    """Update an existing template's fields.

    Only fields that are provided (not None) will be updated.

    Args:
        templates_path: Path to templates.yaml
        template_id: ID of template to update
        title: New title (optional)
        description: New description (optional)
        category: New category (optional)
        tier: New tier (optional)
        tags: New tags (optional)
        features: New features (optional)

    Returns:
        WriteResult indicating success or failure
    """
    errors = []
    warnings = []

    try:
        data = load_yaml_raw(templates_path)
    except Exception as e:
        return WriteResult(success=False, errors=[f"Failed to load YAML: {e}"])

    if data is None:
        return WriteResult(success=False, errors=["Templates file is empty"])

    templates = data.get("templates") or []
    categories = data.get("categories") or []
    category_ids = {c.get("id") for c in categories if isinstance(c, dict)}

    # Find template
    template_index = None
    for i, t in enumerate(templates):
        if isinstance(t, dict) and t.get("id") == template_id:
            template_index = i
            break

    if template_index is None:
        return WriteResult(success=False, errors=[f"Template '{template_id}' not found"])

    template = templates[template_index]

    # Validate category if changing
    if category is not None and category not in category_ids:
        errors.append(f"Category '{category}' does not exist")
        return WriteResult(success=False, errors=errors)

    # Update fields
    if title is not None:
        template["title"] = title
    if description is not None:
        template["description"] = description
    if category is not None:
        template["category"] = category
    if tier is not None:
        template["tier"] = tier
    if tags is not None:
        from ruamel.yaml.comments import CommentedSeq
        template["tags"] = CommentedSeq(tags)
    if features is not None:
        from ruamel.yaml.comments import CommentedSeq
        template["features"] = CommentedSeq(features)

    # Save
    try:
        save_yaml(templates_path, data)
    except Exception as e:
        return WriteResult(success=False, errors=[f"Failed to save YAML: {e}"])

    return WriteResult(success=True, warnings=warnings)


def remove_template(
    templates_path: Path,
    template_id: str,
    force: bool = False,
) -> WriteResult:
    """Remove a template from the registry.

    Args:
        templates_path: Path to templates.yaml
        template_id: ID of template to remove
        force: If True, skip reference check warnings

    Returns:
        WriteResult indicating success or failure
    """
    errors = []
    warnings = []

    try:
        data = load_yaml_raw(templates_path)
    except Exception as e:
        return WriteResult(success=False, errors=[f"Failed to load YAML: {e}"])

    if data is None:
        return WriteResult(success=False, errors=["Templates file is empty"])

    templates = data.get("templates") or []

    # Find template index
    template_index = None
    for i, t in enumerate(templates):
        if isinstance(t, dict) and t.get("id") == template_id:
            template_index = i
            break

    if template_index is None:
        return WriteResult(success=False, errors=[f"Template '{template_id}' not found"])

    # Check for references from other templates
    if not force:
        referencing = []
        for t in templates:
            if not isinstance(t, dict):
                continue
            relates_to = t.get("relates_to") or []
            for rel in relates_to:
                if isinstance(rel, dict) and rel.get("template_id") == template_id:
                    referencing.append(t.get("id", "<unknown>"))
        if referencing:
            warnings.append(
                f"Template '{template_id}' is referenced by: {', '.join(referencing)}. "
                "Use --force to remove anyway."
            )
            return WriteResult(success=False, errors=[], warnings=warnings)

    # Remove template
    del templates[template_index]
    data["templates"] = templates

    # Save
    try:
        save_yaml(templates_path, data)
    except Exception as e:
        return WriteResult(success=False, errors=[f"Failed to save YAML: {e}"])

    return WriteResult(success=True, warnings=warnings)


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

    # Use 'or []' to handle explicit null values (e.g., templates: null)
    # Filter for only dict items to handle malformed data gracefully
    raw_templates = data.get("templates") or []
    templates = [t for t in raw_templates if isinstance(t, dict)]

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
            # Convert to string and handle None values for safe slicing
            template_id = str(t.get("id") or "unknown")[:30]
            title = str(t.get("title") or "Untitled")[:35]
            category = str(t.get("category") or "none")[:20]
            tier = str(t.get("tier") or "none")[:12]
            print(f"{template_id:<30} {title:<35} {category:<20} {tier:<12}")

        print(f"\nTotal: {len(templates)} template(s)")

    return 0


def cmd_add(args: argparse.Namespace) -> int:
    """Handle the add subcommand."""
    templates_path = Path(args.templates) if args.templates else DEFAULT_TEMPLATES_PATH

    if not templates_path.exists():
        print(f"Error: Templates file not found: {templates_path}", file=sys.stderr)
        return 1

    # Parse repo argument
    repo_parts = args.repo.split("/")
    if len(repo_parts) != 2:
        print(f"Error: Invalid repo format '{args.repo}'. Expected 'owner/name'", file=sys.stderr)
        return 1
    repo_owner, repo_name = repo_parts

    # Parse optional lists
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
    features = [f.strip() for f in args.features.split(",")] if args.features else None

    result = add_template(
        templates_path=templates_path,
        template_id=args.id,
        repo_owner=repo_owner,
        repo_name=repo_name,
        title=args.title,
        description=args.description,
        category=args.category,
        tier=args.tier,
        tags=tags,
        features=features,
    )

    if result.errors:
        for error in result.errors:
            print(f"Error: {error}", file=sys.stderr)

    if result.warnings:
        for warning in result.warnings:
            print(f"Warning: {warning}", file=sys.stderr)

    if result.success:
        print(f"Added template '{args.id}' to {templates_path}")
        return 0
    else:
        return 1


def cmd_update(args: argparse.Namespace) -> int:
    """Handle the update subcommand."""
    templates_path = Path(args.templates) if args.templates else DEFAULT_TEMPLATES_PATH

    if not templates_path.exists():
        print(f"Error: Templates file not found: {templates_path}", file=sys.stderr)
        return 1

    # Parse optional lists
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
    features = [f.strip() for f in args.features.split(",")] if args.features else None

    result = update_template(
        templates_path=templates_path,
        template_id=args.id,
        title=args.title,
        description=args.description,
        category=args.category,
        tier=args.tier,
        tags=tags,
        features=features,
    )

    if result.errors:
        for error in result.errors:
            print(f"Error: {error}", file=sys.stderr)

    if result.warnings:
        for warning in result.warnings:
            print(f"Warning: {warning}", file=sys.stderr)

    if result.success:
        print(f"Updated template '{args.id}'")
        return 0
    else:
        return 1


def cmd_remove(args: argparse.Namespace) -> int:
    """Handle the remove subcommand."""
    templates_path = Path(args.templates) if args.templates else DEFAULT_TEMPLATES_PATH

    if not templates_path.exists():
        print(f"Error: Templates file not found: {templates_path}", file=sys.stderr)
        return 1

    result = remove_template(
        templates_path=templates_path,
        template_id=args.id,
        force=args.force,
    )

    if result.errors:
        for error in result.errors:
            print(f"Error: {error}", file=sys.stderr)

    if result.warnings:
        for warning in result.warnings:
            print(f"Warning: {warning}", file=sys.stderr)

    if result.success:
        print(f"Removed template '{args.id}'")
        return 0
    else:
        return 1


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

    # add subcommand
    add_parser = subparsers.add_parser(
        "add",
        help="Add a new template to the registry",
    )
    add_parser.add_argument(
        "--id",
        required=True,
        help="Unique template identifier (lowercase, hyphens allowed)",
    )
    add_parser.add_argument(
        "--repo",
        required=True,
        help="GitHub repository (format: owner/name)",
    )
    add_parser.add_argument(
        "--title",
        required=True,
        help="Display title for the template",
    )
    add_parser.add_argument(
        "--description",
        required=True,
        help="Brief description of the template",
    )
    add_parser.add_argument(
        "--category",
        required=True,
        help="Category ID reference",
    )
    add_parser.add_argument(
        "--tier",
        default="starter",
        choices=["starter", "production", "stable", "beta", "experimental"],
        help="Template tier (default: starter)",
    )
    add_parser.add_argument(
        "--tags",
        help="Comma-separated list of tags",
    )
    add_parser.add_argument(
        "--features",
        help="Comma-separated list of features",
    )
    add_parser.add_argument(
        "--templates",
        help=f"Path to templates.yaml (default: {DEFAULT_TEMPLATES_PATH})",
    )
    add_parser.set_defaults(func=cmd_add)

    # update subcommand
    update_parser = subparsers.add_parser(
        "update",
        help="Update an existing template",
    )
    update_parser.add_argument(
        "id",
        help="Template ID to update",
    )
    update_parser.add_argument(
        "--title",
        help="New title",
    )
    update_parser.add_argument(
        "--description",
        help="New description",
    )
    update_parser.add_argument(
        "--category",
        help="New category",
    )
    update_parser.add_argument(
        "--tier",
        choices=["starter", "production", "stable", "beta", "experimental"],
        help="New tier",
    )
    update_parser.add_argument(
        "--tags",
        help="Comma-separated list of new tags",
    )
    update_parser.add_argument(
        "--features",
        help="Comma-separated list of new features",
    )
    update_parser.add_argument(
        "--templates",
        help=f"Path to templates.yaml (default: {DEFAULT_TEMPLATES_PATH})",
    )
    update_parser.set_defaults(func=cmd_update)

    # remove subcommand
    remove_parser = subparsers.add_parser(
        "remove",
        help="Remove a template from the registry",
    )
    remove_parser.add_argument(
        "id",
        help="Template ID to remove",
    )
    remove_parser.add_argument(
        "--force",
        action="store_true",
        help="Force removal even if referenced by other templates",
    )
    remove_parser.add_argument(
        "--templates",
        help=f"Path to templates.yaml (default: {DEFAULT_TEMPLATES_PATH})",
    )
    remove_parser.set_defaults(func=cmd_remove)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
