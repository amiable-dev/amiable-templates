# ADR-003: Template Configuration System

**Status:** Accepted 2026-01-03
**Date:** 2026-01-03
**Decision Makers:** @amiable-dev/maintainers
**Depends On:** ADR-002 (Site Architecture)
**Council Review:** 2026-01-03 (Tier: Balanced, Models: GPT-5.2, Claude Opus 4.5, Gemini 3 Pro, Grok 4.1)

---

## Context

The amiable-templates site aggregates documentation from multiple template repositories. We need a configuration system that:

1. Defines which templates are included in the site
2. Specifies where to find documentation in each repository
3. Provides metadata for the template grid (description, tags, links)
4. Is easy to maintain and validate
5. Supports future extensibility

### Current State

No configuration system exists. Template information is hardcoded in documentation.

### Goals

1. Single source of truth for template registry
2. Declarative configuration (no code required to add templates)
3. Schema validation to catch errors early
4. Support for categorization and tagging
5. Clear documentation paths for aggregation

## Non-Goals

- Runtime template discovery (build-time is sufficient)
- Template marketplace features (ratings, downloads)
- Template versioning/pinning (always use latest)

## Considered Options

### Option 1: YAML Configuration (Recommended)

Use a YAML file (`templates.yaml`) with JSON Schema validation.

**Pros:**
- Human-readable and easy to edit
- Consistent with MkDocs (mkdocs.yml)
- Good tooling support (schema validation, IDE completion)
- Supports complex nested structures
- Comments allowed for documentation

**Cons:**
- Requires parser (pyyaml)
- YAML syntax can be error-prone

### Option 2: TOML Configuration

Use TOML format, consistent with Railway templates (railway.toml).

**Pros:**
- Consistent with Railway ecosystem
- Simple, unambiguous syntax

**Cons:**
- Less common in Python/MkDocs ecosystem
- Limited nesting capabilities
- No comments in inline tables

### Option 3: JSON Configuration

Use JSON for strict typing and universal compatibility.

**Pros:**
- Strict syntax (catches errors)
- Universal parser support
- Schema validation built-in

**Cons:**
- No comments
- Verbose for humans
- Less readable than YAML

## Decision

Use **YAML configuration** with JSON Schema validation:

### 1. Configuration File: `templates.yaml`

```yaml
version: "1.0"

settings:
  github_api:
    require_token: true
    concurrency: 5
  cache:
    directory: ".cache/templates"
  output:
    docs_directory: "docs/templates"

categories:
  - id: observability
    name: "Observability & Monitoring"
    icon: "material/chart-line"
    description: "LLM observability, tracing, and monitoring stacks"
  - id: ai-infrastructure
    name: "AI Infrastructure"
    icon: "material/brain"
    description: "LLM gateways, embeddings, and AI pipelines"

templates:
  - id: litellm-langfuse-starter
    repo:
      owner: "amiable-dev"
      name: "litellm-langfuse-railway"
    title: "LiteLLM + Langfuse Starter"
    description: "Production-ready LLM gateway with observability"
    category: observability
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
    links:
      railway_template: "https://railway.app/template/..."
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

### 2. Schema Definition: `templates.schema.yaml`

JSON Schema for validation:

```yaml
$schema: "http://json-schema.org/draft-07/schema#"
title: "Amiable Templates Registry"
type: object

required:
  - version
  - templates

properties:
  version:
    type: string
    pattern: "^\\d+\\.\\d+$"

  categories:
    type: array
    items:
      type: object
      required: [id, name]
      properties:
        id:
          type: string
          pattern: "^[a-z][a-z0-9-]*$"
        name:
          type: string
        icon:
          type: string
        description:
          type: string

  templates:
    type: array
    items:
      type: object
      required:
        - id
        - repo
        - title
        - description
        - category
        - directories
      properties:
        id:
          type: string
          pattern: "^[a-z][a-z0-9-]*$"
        # ... full schema
```

### 3. Template Entry Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier (slug) |
| `repo.owner` | Yes | GitHub organization/user |
| `repo.name` | Yes | Repository name |
| `title` | Yes | Display name |
| `description` | Yes | Brief description |
| `category` | Yes | Category ID reference |
| `tags` | No | List of tags for filtering |
| `directories.template` | No | Path to template in repo |
| `directories.docs` | Yes | List of docs to fetch |
| `links.railway_template` | No | Railway deploy URL |
| `links.github` | Yes | GitHub repository URL |
| `features` | No | List of feature highlights |
| `estimated_cost` | No | Cost estimate object |

### 4. Validation

- Run schema validation in CI on PRs
- Validate before aggregation script runs
- Clear error messages for invalid entries

### 5. Extensibility

Future fields can be added without breaking existing entries:
- `status: stable | beta | experimental`
- `relates_to: [template_ids]`
- `version: "1.0.0"` (pin to specific release)

## Consequences

### Positive

1. **Declarative**: Add templates without code changes
2. **Validated**: Schema catches errors before build
3. **Documented**: Self-documenting field structure
4. **Flexible**: Supports varied template structures

### Negative

1. **Manual updates**: Template changes require config updates
2. **Schema maintenance**: Schema must evolve with needs

### Neutral

1. YAML is familiar to the target audience
2. JSON Schema is well-supported but has learning curve

## Implementation Phases

### Phase 1: Core Schema

- [x] Create templates.yaml with initial templates
- [x] Define JSON Schema for validation
- [x] Add validation to CI workflow

### Phase 2: Aggregation Integration

- [x] Aggregation script reads templates.yaml
- [x] Fetch docs based on `directories.docs`
- [x] Generate template grid from config

### Phase 3: Documentation

- [x] Document schema in CONTRIBUTING.md
- [x] Add examples for common patterns
- [x] IDE schema configuration

## Compliance / Validation

- [x] Schema validates all current templates
- [x] Invalid entries produce clear error messages
- [x] CI fails on schema violations
- [x] Aggregation script handles missing optional fields

---

## LLM Council Review Summary

**Reviewed:** 2026-01-03
**Tier:** Balanced (4 models: GPT-5.2, Claude Opus 4.5, Gemini 3 Pro, Grok 4.1)

### Verdict: Accepted

Data flow from Definition (ADR-003) → Aggregation (ADR-006) → Presentation (ADR-002) is logical and well-designed.

### Key Findings Incorporated

| Finding | Resolution |
|---------|------------|
| Schema validation needed as pre-commit hook | Added `check-jsonschema` recommendation to ADR-005 |
| Cache key should combine YAML hash and commit SHA | Implemented in aggregation script |
| Need explicit handling for varying upstream structures | Added flexible `directories.docs` path mapping |

### Dissenting Views

- All models agreed YAML configuration is appropriate for this use case.

---

## References

- [JSON Schema](https://json-schema.org/)
- [PyYAML](https://pyyaml.org/)
- [ADR-003: Cross-Project ADR Aggregation](https://amiable.dev/docs/adrs/ADR-003-cross-project-adr-aggregation) (pattern reference)
