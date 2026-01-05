# Template Management Guide

This guide covers managing the template registry using the Template Manager CLI.

## Overview

The `template_manager.py` CLI tool provides commands for managing `templates.yaml`:

| Command | Description |
|---------|-------------|
| `validate` | Validate templates against schema and semantic rules |
| `list` | List templates with optional filtering |
| `add` | Add a new template to the registry |
| `update` | Update an existing template's fields |
| `remove` | Remove a template from the registry |

## Quick Start

```bash
# Validate the registry
python scripts/template_manager.py validate

# List all templates
python scripts/template_manager.py list

# Add a new template
python scripts/template_manager.py add \
  --id my-template \
  --repo owner/repo \
  --title "My Template" \
  --description "Description" \
  --category observability
```

## Validation

The tool provides three levels of validation:

### Level 1: Schema Validation

Validates against `templates.schema.yaml`:
- Required fields present
- Correct data types
- Valid ID patterns

```bash
python scripts/template_manager.py validate
```

### Level 2: Semantic Validation

Checks logical consistency:
- Unique template IDs
- Valid category references
- Valid `relates_to` references
- HTTPS URLs (warns on HTTP)

```bash
python scripts/template_manager.py validate
```

### Level 3: Network Validation

Checks URL reachability (opt-in):
- GitHub repository existence
- Link URLs respond to HEAD requests

```bash
python scripts/template_manager.py validate --deep
```

Network issues are reported as **warnings**, not errors.

## Commands

### validate

Validate the templates registry.

```bash
# Basic validation (Level 1 + 2)
python scripts/template_manager.py validate

# With network checks (Level 1 + 2 + 3)
python scripts/template_manager.py validate --deep

# Custom paths
python scripts/template_manager.py validate \
  --templates /path/to/templates.yaml \
  --schema /path/to/schema.yaml
```

**Options:**
- `--templates PATH`: Path to templates.yaml (default: `templates.yaml`)
- `--schema PATH`: Path to schema file (default: `templates.schema.yaml`)
- `--deep`: Include network validation (URL reachability)

### list

List templates in the registry.

```bash
# Text format (human-readable)
python scripts/template_manager.py list

# JSON format (for scripting)
python scripts/template_manager.py list --format json

# Filter by category
python scripts/template_manager.py list --category observability

# Filter by tier
python scripts/template_manager.py list --tier production
```

**Options:**
- `--format {text,json}`: Output format (default: text)
- `--category CAT`: Filter by category ID
- `--tier TIER`: Filter by tier (starter, production, stable, beta, experimental)
- `--templates PATH`: Path to templates.yaml

### add

Add a new template to the registry.

```bash
python scripts/template_manager.py add \
  --id my-new-template \
  --repo amiable-dev/my-repo \
  --title "My New Template" \
  --description "A brief description" \
  --category observability \
  --tier starter \
  --tags "tag1,tag2,tag3" \
  --features "Feature 1,Feature 2"
```

**Required options:**
- `--id ID`: Unique template identifier (lowercase, hyphens allowed)
- `--repo OWNER/NAME`: GitHub repository (format: owner/name)
- `--title TITLE`: Display title
- `--description DESC`: Brief description
- `--category CAT`: Category ID (must exist)

**Optional:**
- `--tier TIER`: Template tier (default: starter)
- `--tags TAGS`: Comma-separated tags
- `--features FEATURES`: Comma-separated features
- `--templates PATH`: Path to templates.yaml

### update

Update an existing template.

```bash
# Update title
python scripts/template_manager.py update my-template \
  --title "New Title"

# Update multiple fields
python scripts/template_manager.py update my-template \
  --description "New description" \
  --tier production

# Update tags
python scripts/template_manager.py update my-template \
  --tags "new-tag1,new-tag2"
```

**Options:**
- `--title TITLE`: New title
- `--description DESC`: New description
- `--category CAT`: New category
- `--tier TIER`: New tier
- `--tags TAGS`: New tags (comma-separated)
- `--features FEATURES`: New features (comma-separated)
- `--templates PATH`: Path to templates.yaml

### remove

Remove a template from the registry.

```bash
# Remove (will warn if referenced by other templates)
python scripts/template_manager.py remove my-template

# Force remove (ignore references)
python scripts/template_manager.py remove my-template --force
```

**Options:**
- `--force`: Force removal even if other templates reference it
- `--templates PATH`: Path to templates.yaml

## Makefile Integration

Common operations are available via `make`:

```bash
make validate        # Run validation (Level 1 + 2)
make validate-deep   # Run validation with network checks
make templates       # List all templates
make templates-json  # List templates as JSON
make template-add    # Add template interactively
make help           # Show all available targets
```

## Using with Claude Code

If you're using Claude Code, the template-registry skill provides guided assistance:

1. The skill is located in `.claude/skills/template-registry/`
2. Ask Claude to "add a new template" or "validate templates"
3. Claude uses the CLI tool with proper validation

See `.claude/skills/template-registry/SKILL.md` for details.

## Workflow Example

### Adding a New Template

```bash
# 1. Create a feature branch
git checkout -b add-my-template

# 2. Add the template
python scripts/template_manager.py add \
  --id my-template \
  --repo my-org/my-repo \
  --title "My Template" \
  --description "Template description" \
  --category observability \
  --tier starter

# 3. Validate
python scripts/template_manager.py validate

# 4. Validate with network checks (optional)
python scripts/template_manager.py validate --deep

# 5. Commit and push
git add templates.yaml
git commit -m "feat: add my-template to registry"
git push -u origin add-my-template

# 6. Create PR
gh pr create --title "Add my-template" --body "Adds new template..."
```

## Error Messages

### "Category does not exist"

The specified category ID doesn't exist. List available categories:

```bash
python scripts/template_manager.py list --format json | jq '.[].category' | sort -u
```

### "Template already exists"

A template with this ID already exists. Use `update` instead:

```bash
python scripts/template_manager.py update existing-id --title "New Title"
```

### "Invalid template ID"

Template IDs must match pattern `^[a-z][a-z0-9-]*$`:
- Start with lowercase letter
- Contain only lowercase letters, numbers, hyphens

Valid: `my-template`, `app-v2`, `litellm-starter`
Invalid: `My-Template`, `app_v2`, `123-template`

### "Template not found"

The specified template ID doesn't exist. List templates:

```bash
python scripts/template_manager.py list
```

## Security

The CLI includes security protections:

- **Symlink rejection**: Prevents reading/writing through symlinks
- **Input validation**: GitHub owner/repo patterns prevent injection
- **SSRF prevention**: Schema validation blocks remote `$ref` resolution
- **Atomic writes**: Temp file + rename prevents partial writes

## See Also

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [ADR-007](adrs/ADR-007-template-management-tooling.md) - Design documentation
- [templates.schema.yaml](../templates.schema.yaml) - JSON Schema
