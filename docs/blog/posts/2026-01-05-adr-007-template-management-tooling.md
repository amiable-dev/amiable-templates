---
date: 2026-01-05
authors:
  - amiable-dev
categories:
  - ADRs
  - Architecture
  - Developer Experience
tags:
  - adr-007
  - cli
  - tooling
  - claude-code
  - automation
---

# Building Template Management Tooling: ADR-007

How we built a CLI tool and Claude Code skill to manage our template registry with three levels of validation.

<!-- more -->

## The Problem

ADR-003 gave us a declarative template registry (`templates.yaml`), but managing it was painful:

1. **Error-prone**: Nested YAML structures are easy to mess up
2. **Undiscoverable**: New contributors didn't know required fields
3. **No feedback**: Errors only surfaced during CI builds
4. **Manual validation**: Run JSON Schema checks by hand

We needed tooling for both humans and LLMs to manage templates reliably.

## The Solution: Hybrid Approach

We evaluated four options:

| Option | Verdict |
|--------|---------|
| Claude Code Skills only | Limited to Claude Code users |
| MCP Server | Overkill for 3 templates |
| Makefile only | No guided prompts |
| **Hybrid (Skills + Makefile + CLI)** | Best of all worlds |

The hybrid approach uses a **single Python CLI** as the canonical implementation, with both Skills and Makefile as interfaces.

## The CLI: `template_manager.py`

All operations go through one entry point:

```bash
# Validation
python scripts/template_manager.py validate
python scripts/template_manager.py validate --deep  # Network checks

# List templates
python scripts/template_manager.py list
python scripts/template_manager.py list --category observability --format json

# CRUD operations
python scripts/template_manager.py add --id my-template --repo owner/repo ...
python scripts/template_manager.py update my-template --tier production
python scripts/template_manager.py remove old-template
```

### Why One CLI?

- **Single source of truth**: Skills and Makefile both call the same code
- **Testable**: 54 unit tests cover all operations
- **Consistent**: Same validation logic everywhere

## Three Levels of Validation

Not all validation is equal. We separated checks by speed and importance:

| Level | When | What | Blocking? |
|-------|------|------|-----------|
| **Level 1: Schema** | Always | JSON Schema conformance, types, required fields | Yes |
| **Level 2: Semantic** | Always | Unique IDs, valid category refs, HTTPS URLs | Yes |
| **Level 3: Network** | `--deep` only | URL reachability, GitHub repo existence | No (warning) |

Level 3 is opt-in because network checks are slow and external services can be flaky:

```bash
$ python scripts/template_manager.py validate --deep

Network warnings:
  - Template 'litellm-langfuse-starter' links.railway_template not found (404)
Validation passed: templates.yaml
```

The template is still valid—we just warn about the broken link.

## Claude Code Skill Integration

For LLM-assisted workflows, we created a skill at `.claude/skills/template-registry/`:

```
template-registry/
├── SKILL.md           # Main instructions (safety rules, CLI commands)
├── schema-reference.md # Field documentation
└── examples.md        # Common patterns
```

The skill teaches Claude to use the CLI safely:

```markdown
## Important Safety Rules
1. ALWAYS run validation before any write operation
2. NEVER commit directly to main - create a branch/PR
3. Treat all LLM outputs as untrusted until validated
```

Now you can ask Claude: "Add a new template for my-awesome-project" and it will:

1. Use the CLI with proper arguments
2. Run validation
3. Create a branch and PR

## Security Hardening

LLM-assisted editing introduces risks. We added multiple protections:

### Input Validation

```python
# Reject malformed GitHub owner/repo names
GITHUB_OWNER_PATTERN = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$")
GITHUB_REPO_PATTERN = re.compile(r"^[a-zA-Z0-9._-]{1,100}$")
```

### Symlink Protection

```python
# Reject symlinks to prevent LFI attacks
fd = os.open(str(path), os.O_RDONLY | os.O_NOFOLLOW)
```

### YAML Hardening

```python
yaml.allow_duplicate_keys = False  # Catch accidental overwrites
```

### Atomic Writes

```python
# Write to temp file, then atomic rename
fd, temp_path = tempfile.mkstemp(dir=path.parent)
# ... write content ...
os.replace(temp_path, path)  # Atomic on POSIX
```

## Makefile Integration

For automation and CI, everything is available via `make`:

```bash
make validate        # Level 1 + 2
make validate-deep   # Level 1 + 2 + 3
make templates       # List all
make templates-json  # JSON output
make help           # Show all targets
```

The `build` target runs validation first:

```makefile
build: validate
	python scripts/aggregate_templates.py
	mkdocs build --strict
```

## Pre-commit Hook

Validation runs automatically before commits:

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: template-manager-validate
      name: Validate templates.yaml (semantic)
      entry: python scripts/template_manager.py validate
      files: ^templates\.yaml$
```

Now invalid templates can't even be committed locally.

## What We Learned

1. **One CLI, many interfaces**: Skills and Makefile are just wrappers
2. **Tiered validation saves time**: Fast checks always, slow checks on demand
3. **LLMs need guardrails**: Validation-first prevents hallucinated YAML
4. **Atomic operations matter**: Temp file + rename prevents corruption

## Implementation Stats

- **4 phases** over 2 days
- **54 tests** with full coverage
- **1,053 lines** of Python
- **16 GitHub issues** tracked and closed

## What's Next

- **MCP Server**: Reconsider at 20+ templates (current: 3)
- **Template Linting**: Check for common misconfigurations
- **Auto-sync**: Fetch metadata from Railway API

---

**Links:**

- [ADR-007: Template Management Tooling](https://github.com/amiable-dev/amiable-templates/blob/main/docs/adrs/ADR-007-template-management-tooling.md)
- [Template Management Guide](https://github.com/amiable-dev/amiable-templates/blob/main/docs/TEMPLATE_MANAGEMENT.md)
- [template_manager.py](https://github.com/amiable-dev/amiable-templates/blob/main/scripts/template_manager.py)
