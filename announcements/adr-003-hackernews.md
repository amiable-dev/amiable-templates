# ADR-003 Hacker News Announcement

**Title:** Validating YAML config files with JSON Schema strict property checks

**URL:** https://amiable-dev.github.io/amiable-templates/blog/2026/01/03/designing-the-template-registry-adr-003/

**Comment to post with submission:**

We built a YAML-based template registry. The problem: YAML parsers are forgiving. A typo like `featurs` instead of `features` passes silently—the downstream Python code calls `.get('features', [])` and gets an empty list.

The fix: JSON Schema with `additionalProperties: false`. Now unknown fields cause explicit failures.

Pipeline: `templates.yaml` → PyYAML → Python dict → `check-jsonschema` → aggregation script

One limitation worth noting: JSON Schema's `uniqueItems` keyword works on primitive arrays, but can't validate that a specific field (like `id`) is unique across an array of objects. That's a global constraint the schema evaluates locally. We added a Python one-liner to check for duplicate template IDs.

We considered typed config languages (Cue, Dhall) but stuck with YAML for consistency with mkdocs.yml and lower barrier to contribution.

Source: https://github.com/amiable-dev/amiable-templates
