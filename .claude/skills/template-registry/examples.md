# Template Examples

Common patterns and examples for managing templates.

## Minimal Template

The simplest valid template with only required fields:

```yaml
- id: my-minimal-template
  repo:
    owner: "my-org"
    name: "my-repo"
  title: "Minimal Template"
  description: "A basic template example"
  category: observability
  directories:
    docs:
      - path: "README.md"
        target: "overview.md"
```

**CLI command:**
```bash
python scripts/template_manager.py add \
  --id my-minimal-template \
  --repo my-org/my-repo \
  --title "Minimal Template" \
  --description "A basic template example" \
  --category observability
```

## Full-Featured Template

A complete template with all optional fields:

```yaml
- id: litellm-langfuse-starter
  repo:
    owner: "amiable-dev"
    name: "litellm-langfuse-railway"

  title: "LiteLLM + Langfuse Starter"
  description: "Production-ready LLM gateway with full observability."
  value_proposition: "Unified API for 100+ LLM providers with tracing"

  category: observability
  tier: starter

  tags:
    - litellm
    - langfuse
    - observability

  directories:
    template: "starter"
    docs:
      - path: "starter/README.md"
        target: "overview.md"
        sidebar_label: "Overview"
      - path: "starter/SETUP.md"
        target: "setup.md"
        sidebar_label: "Setup Guide"
    adrs:
      - path: "docs/adr"

  links:
    railway_template: "https://railway.app/template/abc123"
    github: "https://github.com/amiable-dev/litellm-langfuse-railway"

  features:
    - "100+ LLM Providers"
    - "Cost Tracking"
    - "Full Tracing"

  estimated_cost:
    min: 29
    max: 68
    currency: "USD"
    period: "month"
```

## Related Templates (Starter/Production Pair)

When you have starter and production versions:

**Starter version:**
```yaml
- id: my-template-starter
  repo:
    owner: "my-org"
    name: "my-template"
  title: "My Template Starter"
  description: "Simplified version for development"
  category: ai-infrastructure
  tier: starter
  directories:
    template: "starter"
    docs:
      - path: "starter/README.md"
        target: "overview.md"
  relates_to:
    - template_id: my-template-production
      relationship: starter_version
```

**Production version:**
```yaml
- id: my-template-production
  repo:
    owner: "my-org"
    name: "my-template"
  title: "My Template Production"
  description: "Full-featured production version"
  category: ai-infrastructure
  tier: production
  directories:
    template: "production"
    docs:
      - path: "production/README.md"
        target: "overview.md"
  relates_to:
    - template_id: my-template-starter
      relationship: production_version
```

## Common Workflows

### Add a New Template

```bash
# 1. Create a branch
git checkout -b add-new-template

# 2. Add the template
python scripts/template_manager.py add \
  --id my-new-template \
  --repo amiable-dev/my-repo \
  --title "My New Template" \
  --description "Template description here" \
  --category observability \
  --tier starter \
  --tags "tag1,tag2,tag3"

# 3. Validate
python scripts/template_manager.py validate

# 4. Commit and push
git add templates.yaml
git commit -m "feat: add my-new-template to registry"
git push -u origin add-new-template

# 5. Create PR
gh pr create --title "Add my-new-template" --body "Adds new template for..."
```

### Update Template Description

```bash
python scripts/template_manager.py update my-template \
  --description "Updated description with more detail"
```

### Update Template Tier

```bash
# Promote from starter to stable
python scripts/template_manager.py update my-template \
  --tier stable
```

### Remove Deprecated Template

```bash
# Check if other templates reference it
python scripts/template_manager.py remove old-template

# If referenced, force removal
python scripts/template_manager.py remove old-template --force
```

### List Templates by Category

```bash
# List all observability templates
python scripts/template_manager.py list --category observability

# List as JSON for scripting
python scripts/template_manager.py list --category observability --format json
```

### Validate Before Committing

```bash
# Quick validation (schema + semantic)
python scripts/template_manager.py validate

# Or use make
make validate
```

## See Also

- [SKILL.md](SKILL.md) - Quick reference and safety rules
- [schema-reference.md](schema-reference.md) - Complete field documentation
