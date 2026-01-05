# Template Registry Management

Manage templates.yaml registry entries with schema validation.
Use for adding, updating, or removing Railway deployment templates.

## Safety Rules

1. **ALWAYS validate before writing**: Run `make validate` after any changes
2. **Use the CLI tool**: Never edit templates.yaml directly - use `scripts/template_manager.py`
3. **Create branches for changes**: Never commit template changes directly to main
4. **Verify category exists**: Before adding a template, ensure the category ID is valid

## Quick Operations

### Validate Registry
```bash
python scripts/template_manager.py validate
```

### List Templates
```bash
# Text format
python scripts/template_manager.py list

# JSON format
python scripts/template_manager.py list --format json

# Filter by category
python scripts/template_manager.py list --category observability
```

### Add New Template
```bash
python scripts/template_manager.py add \
  --id my-new-template \
  --repo owner/repo-name \
  --title "My New Template" \
  --description "Description of the template" \
  --category observability \
  --tier starter
```

### Update Template
```bash
python scripts/template_manager.py update my-template \
  --title "Updated Title" \
  --description "Updated description"
```

### Remove Template
```bash
# Check for references first (warns if other templates reference it)
python scripts/template_manager.py remove my-template

# Force removal even if referenced
python scripts/template_manager.py remove my-template --force
```

## Workflow: Adding a New Template

1. **Check existing categories**:
   ```bash
   python scripts/template_manager.py list --format json | jq '.[].category' | sort -u
   ```

2. **Add the template**:
   ```bash
   python scripts/template_manager.py add \
     --id my-template \
     --repo amiable-dev/my-repo \
     --title "My Template" \
     --description "Template description" \
     --category observability \
     --tier starter
   ```

3. **Validate the registry**:
   ```bash
   python scripts/template_manager.py validate
   ```

4. **Commit and create PR**:
   ```bash
   git checkout -b add-my-template
   git add templates.yaml
   git commit -m "feat: add my-template to registry"
   git push -u origin add-my-template
   gh pr create --title "Add my-template" --body "Adds new template for..."
   ```

## Reference Documentation

- [Schema Reference](schema-reference.md) - Complete field documentation
- [Examples](examples.md) - Common template patterns

## Validation Levels

| Level | Command | Checks |
|-------|---------|--------|
| Schema | `validate` | JSON Schema conformance, required fields, types |
| Semantic | `validate` | Unique IDs, category references, relates_to references |
| Network | `validate --deep` | URL reachability (future) |

## Common Errors

### "Category does not exist"
The category ID doesn't match any defined category. Check available categories:
```bash
grep -A1 "^  - id:" templates.yaml
```

### "Template already exists"
A template with this ID already exists. Use `update` instead of `add`.

### "Invalid template ID"
Template IDs must be lowercase letters, numbers, and hyphens, starting with a letter.
Example valid IDs: `my-template`, `litellm-starter`, `app2`
