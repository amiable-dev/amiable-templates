# ADR-003 LinkedIn Announcement

How many production issues trace back to a config typo?

We built a template registry where adding a new entry is just YAML. The problem: YAML parsers are forgiving. A typo like `featurs` instead of `features` passes silently—the downstream code just gets an empty value.

**The fix:** JSON Schema with `additionalProperties: false`

This one line catches typos that would otherwise slip through:

```
$.templates[0]: 'featurs' was unexpected
```

**Why we also added Python:**

JSON Schema validates structure locally—each object in isolation. But it can't check that all template IDs are unique *across* an array of objects. That's a global constraint. So we added a Python one-liner in CI:

```python
ids = [t['id'] for t in config.get('templates', [])]
if len(ids) != len(set(ids)):
    exit(1)
```

The result: developers get instant feedback on PRs instead of discovering issues after merge.

Full write-up with Mermaid diagrams: https://amiable-dev.github.io/amiable-templates/blog/2026/01/03/designing-the-template-registry-adr-003/

What validation patterns have saved you from silent failures?
