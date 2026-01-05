# Template Schema Reference

Complete field documentation for `templates.yaml` entries.

## Template Entry Fields

### Required Fields

| Field | Type | Pattern | Description |
|-------|------|---------|-------------|
| `id` | string | `^[a-z][a-z0-9-]*$` | Unique identifier (lowercase, hyphens allowed) |
| `repo.owner` | string | - | GitHub organization or user |
| `repo.name` | string | - | Repository name |
| `title` | string | - | Display title for template |
| `description` | string | - | Brief description for template grid |
| `category` | string | `^[a-z][a-z0-9-]*$` | Category ID reference (must exist) |
| `directories.docs` | array | - | List of documentation paths to fetch |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `tier` | enum | Template maturity: `starter`, `production`, `stable`, `beta`, `experimental` |
| `tags` | array[string] | Tags for filtering/search |
| `value_proposition` | string | One-line value proposition |
| `features` | array[string] | Feature highlights for template card |
| `links.github` | string (URI) | GitHub repository URL |
| `links.railway_template` | string (URI) | Railway deploy URL |
| `estimated_cost` | object | Cost estimate (see below) |
| `relates_to` | array | Relationships to other templates |
| `directories.template` | string | Path to template directory in repo |
| `directories.adrs` | array | ADR directory paths |

## Field Details

### `id`
Unique identifier for the template. Used in URLs and references.

**Constraints:**
- Must start with a lowercase letter
- Can contain lowercase letters, numbers, and hyphens
- Examples: `litellm-starter`, `my-app`, `prod-v2`

### `repo`
GitHub repository information.

```yaml
repo:
  owner: "amiable-dev"      # GitHub org or user
  name: "my-template-repo"  # Repository name
```

### `category`
Must reference an existing category ID from the `categories` section.

**Available categories** (check templates.yaml for current list):
- `observability` - Observability & Monitoring
- `ai-infrastructure` - AI Infrastructure

### `tier`
Template maturity level:

| Tier | Description |
|------|-------------|
| `starter` | Simplified version for learning/development |
| `production` | Full-featured production-ready version |
| `stable` | Proven stable in production |
| `beta` | Feature complete but may have issues |
| `experimental` | Early development, may change significantly |

### `directories.docs`
List of documentation files to aggregate.

```yaml
directories:
  docs:
    - path: "README.md"           # Source path in repo
      target: "overview.md"       # Target filename in docs
      sidebar_label: "Overview"   # Optional: sidebar display name
    - path: "docs/setup.md"
      target: "setup.md"
```

### `links`
External links for the template.

```yaml
links:
  github: "https://github.com/owner/repo"
  railway_template: "https://railway.app/template/abc123"
```

### `features`
List of feature highlights shown on template card.

```yaml
features:
  - "100+ LLM Providers"
  - "Cost Tracking"
  - "Full Tracing"
```

### `estimated_cost`
Monthly cost estimate for running the template.

```yaml
estimated_cost:
  min: 29         # Minimum monthly cost
  max: 68         # Maximum monthly cost
  currency: "USD" # Currency (default: USD)
  period: "month" # Billing period: month or year
```

### `relates_to`
Relationships between templates.

```yaml
relates_to:
  - template_id: "litellm-starter"
    relationship: production_version
```

**Relationship types:**
| Type | Description |
|------|-------------|
| `production_version` | This is the production version of another template |
| `starter_version` | This is the starter/simplified version |
| `alternative` | Alternative implementation |
| `depends_on` | Requires this other template |

## Category Fields

Categories are defined in the `categories` section.

```yaml
categories:
  - id: observability          # Required: unique identifier
    name: "Observability"      # Required: display name
    icon: "material/chart-line" # Optional: Material icon
    description: "..."          # Optional: description
```

## Validation Rules

1. **Unique IDs**: Template IDs must be unique across all templates
2. **Valid Categories**: Category references must exist in `categories` section
3. **Valid Relations**: `relates_to.template_id` must reference existing templates
4. **URL Schemes**: Links should use HTTPS (HTTP generates warning)
5. **Required Fields**: All required fields must be present

## See Also

- [SKILL.md](SKILL.md) - Quick operations and workflows
- [examples.md](examples.md) - Common template patterns
- [templates.schema.yaml](../../../templates.schema.yaml) - JSON Schema source
