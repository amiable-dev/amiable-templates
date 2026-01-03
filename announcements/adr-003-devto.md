# ADR-003 Dev.to Announcement

**Title:** Stop Silent Config Failures: Validating YAML with JSON Schema

**Tags:** yaml, jsonschema, validation, devops, python

---

We built a YAML-based template registry. The problem? YAML parsers are forgiving. Typos pass silently.

## The Silent Failure

```yaml
templates:
  - id: my-template
    repo:
      owner: "amiable-dev"
      name: "my-repo"
    title: "My Template"
    description: "A template"
    category: observability
    directories:
      docs:
        - path: "README.md"
          target: "overview.md"
    featurs:  # Typo!
      - "Feature 1"
```

Without strict validation, this just gets ignored. The aggregation script calls `.get('features', [])` and returns an empty list. Your template appears on the site with no features listed. No error, no warning.

## The Pipeline

```
templates.yaml → PyYAML → Python dict → check-jsonschema → aggregation
```

We use `check-jsonschema` to validate against a JSON Schema before the aggregation script runs.

## The Fix: additionalProperties: false

```yaml
# templates.schema.yaml
properties:
  templates:
    items:
      type: object
      additionalProperties: false  # This line!
      required:
        - id
        - repo
```

Now the schema rejects unknown fields:

```
$.templates[0]: Additional properties are not allowed ('featurs' was unexpected)
```

## What JSON Schema Can't Do

JSON Schema validates structure locally—each object in isolation. But `uniqueItems` only works for primitive arrays, not for checking that a specific field (`id`) is unique across objects.

Our solution: a Python check in CI:

```python
ids = [t['id'] for t in config.get('templates', [])]
duplicates = [id for id in ids if ids.count(id) > 1]
if duplicates:
    print(f"Duplicate template IDs: {set(duplicates)}")
    exit(1)
```

## The CI Step

```yaml
# .github/workflows/validate.yml
- name: Validate templates.yaml schema
  run: check-jsonschema --schemafile templates.schema.yaml templates.yaml

- name: Validate unique template IDs
  run: python -c "..." # the script above
```

## Why Not Pydantic?

Pydantic would work, but we wanted validation to run without importing Python code. `check-jsonschema` is a standalone CLI tool—it validates the YAML file directly against the schema file. No Python imports needed.

## The Takeaway

1. Use `additionalProperties: false` to catch typos
2. Validate on PRs, not just deploys
3. Add Python checks for global constraints JSON Schema can't express

Full ADR: https://amiable-dev.github.io/amiable-templates/blog/2026/01/03/designing-the-template-registry-adr-003/
