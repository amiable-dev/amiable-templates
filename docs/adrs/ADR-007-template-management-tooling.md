# ADR-007: Template Management Tooling

**Status:** Accepted 2026-01-04
**Date:** 2026-01-04
**Decision Makers:** @amiable-dev/maintainers
**Depends On:** ADR-003 (Template Configuration System)
**Council Review:** 2026-01-04 (Tier: Balanced, Models: GPT-5.2, Claude Sonnet 4.5, Gemini 3, Grok 4)

---

## Context

ADR-003 established a YAML-based template configuration system (`templates.yaml`) with JSON Schema validation. While the schema is well-defined, managing template entries requires manual YAML editing, which is:

1. **Error-prone**: Complex nested structures are easy to misconfigure
2. **Undiscoverable**: New contributors don't know the required fields
3. **Inconsistent**: Different contributors may structure entries differently
4. **Time-consuming**: Manual validation and testing cycles

We need tooling to help both humans and LLMs manage template registry entries reliably.

### Current State

- `templates.yaml` with 3 template entries
- `templates.schema.yaml` for validation
- `check-jsonschema` pre-commit hook for CI validation
- No interactive tooling for CRUD operations

### Goals

1. Provide guided template creation/update workflows
2. Enable LLM-assisted template management via Claude Code
3. Reduce errors through validation-first operations
4. Maintain human-readable YAML (no abstraction layer)
5. Support both interactive and automated workflows

### Non-Goals

- Replace direct YAML editing (power users should still edit directly)
- Build a web UI for template management
- Implement a database backend (file-based is sufficient)
- Create a public API for external template submissions
- Template preview/testing (belongs in integration test suite)
- GUI tool (CLI/Skills sufficient for current team size)

## Considered Options

### Option 1: Claude Code Skills

Create a dedicated skill in `.claude/skills/template-registry/` that teaches Claude how to manage `templates.yaml` entries with validation.

**Pros:**
- Zero runtime dependencies (markdown + scripts)
- Progressive disclosure reduces context overhead
- Scripts execute without loading into context
- Native Claude Code integration
- Validation enforced before any write

**Cons:**
- Requires Claude Code (not usable by other LLMs)
- Limited to Claude Code sessions (not CI/automation)

### Option 2: MCP Server

Implement a Model Context Protocol server exposing template CRUD operations as tools.

**Pros:**
- Protocol-level validation and error handling
- Works with any MCP-compatible client
- Audit logging built-in
- Atomic operations prevent corruption

**Cons:**
- Significant development overhead
- Requires running server process
- Overkill for current scale (3 templates)
- Additional infrastructure to maintain

### Option 3: Makefile Commands

Provide Makefile targets for common operations (validate, add-template, etc.).

**Pros:**
- Universal (works everywhere)
- Familiar to developers
- Easy to integrate with CI
- No special tooling required

**Cons:**
- Limited interactivity (no guided prompts)
- Scripts must be written and maintained
- Less discoverable than skills

### Option 4: Hybrid (Skills + Makefile)

Combine Skills for LLM-assisted workflows with Makefile for automation/CI.

**Pros:**
- Best of both worlds
- Skills for interactive development
- Makefile for CI/CD and scripting
- Single CLI tool shared between both

**Cons:**
- Two interfaces to coordinate (mitigated by shared CLI)

## Decision

Implement **Option 4: Hybrid (Skills + Makefile)** with a **single Python CLI tool** as the canonical implementation.

### MCP Server Rejection Rationale

- Current scale: 3 templates (overhead > benefit)
- No multi-client scenarios identified
- Can be added later without breaking changes
- **Threshold for reconsideration:** >20 templates OR external API consumption needs

### 1. Single CLI Tool: `scripts/template_manager.py`

All operations go through a single entry point with subcommands:

```bash
# Validation
python scripts/template_manager.py validate
python scripts/template_manager.py validate --deep  # Include network checks

# List templates
python scripts/template_manager.py list
python scripts/template_manager.py list --category observability --format json

# Add template (interactive or with args)
python scripts/template_manager.py add --interactive
python scripts/template_manager.py add --id my-template --title "My Template" ...

# Update template
python scripts/template_manager.py update my-template --field description --value "New description"

# Remove template
python scripts/template_manager.py remove my-template --confirm

# Dry-run mode (preview changes without writing)
python scripts/template_manager.py add --interactive --dry-run
```

**Critical Implementation Detail:** Use `ruamel.yaml` (not PyYAML) to preserve comments, block styles, and key ordering. This ensures manual edits and tool-generated edits produce clean diffs.

### 2. Skill: Template Registry Management

Location: `.claude/skills/template-registry/`

```
template-registry/
├── SKILL.md                 # Main skill instructions (calls CLI)
├── schema-reference.md      # Field documentation from ADR-003
└── examples.md              # Common patterns and templates
```

**SKILL.md Structure:**

```text
---
name: template-registry
description: |
  Manage templates.yaml registry entries with schema validation.
  Use for adding, updating, or removing Railway deployment templates.
  Keywords: template, registry, yaml, add template, update template, validate
allowed-tools: Read, Bash(python:scripts/template_manager.py*)
---

# Template Registry Management

## Important Safety Rules
1. ALWAYS run validation before any write operation
2. ALWAYS use --dry-run first to preview changes
3. NEVER commit directly to main - create a branch/PR
4. Treat all LLM outputs as untrusted until validated

## Quick Operations

### Validate Registry
    python scripts/template_manager.py validate

### Add New Template
    python scripts/template_manager.py add --interactive --dry-run
    # Review output, then:
    python scripts/template_manager.py add --interactive

## Reference
For schema definitions, see schema-reference.md
For examples, see examples.md
```

### 3. Makefile Targets

```makefile
# Validation
.PHONY: validate
validate: ## Validate templates.yaml against schema
	@python scripts/template_manager.py validate

.PHONY: validate-deep
validate-deep: ## Validate with network checks (URL reachability)
	@python scripts/template_manager.py validate --deep

# List templates
.PHONY: templates
templates: ## List all templates
	@python scripts/template_manager.py list

.PHONY: templates-json
templates-json: ## List templates as JSON
	@python scripts/template_manager.py list --format json

# Template operations
.PHONY: template-add
template-add: ## Add a new template interactively
	@python scripts/template_manager.py add --interactive

.PHONY: template-rollback
template-rollback: ## Rollback last template change (requires COMMIT=<hash>)
	@git revert $(COMMIT) --no-edit

# Development
.PHONY: serve
serve: ## Start development server
	mkdocs serve

.PHONY: build
build: validate ## Full build with validation
	python scripts/aggregate_templates.py
	mkdocs build --strict

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
```

### 4. Interface Responsibilities

| Task | Primary Interface | Secondary | Rationale |
|------|------------------|-----------|-----------|
| Add template | Skill | Makefile | Interactive fields benefit from LLM guidance |
| Validate | Both | - | Fast feedback in all contexts |
| Bulk operations | Makefile | - | Scripting/CI efficiency |
| Remove template | Skill | Makefile | Safety from confirmation prompts |
| List/query | Skill | Makefile (JSON) | Human vs machine consumption |

### 5. Validation Levels

| Level | When | Checks | Blocking |
|-------|------|--------|----------|
| **Level 1: Schema** | Always | JSON Schema conformance, required fields, types | Yes |
| **Level 2: Semantic** | Pre-commit | Unique IDs, category references exist, URL format validity | Yes |
| **Level 3: Network** | CI only (`--deep`) | URL reachability (HEAD requests), repo existence | No (warning) |

**Out of Scope:** Template functionality testing (belongs in integration tests)

## Security Considerations

### LLM-Assisted Modification Risks

1. **Prompt Injection:** Skills validate ALL changes against schema (no blind writes)
2. **Hallucinated Data:** LLM outputs treated as untrusted until validated
3. **Malicious URLs:** Validation checks URL schemes (https:// only for links)
4. **YAML Injection:** Use `ruamel.yaml` with safe loading (no arbitrary code execution)
5. **Audit Trail:** Git history is authoritative record

### Mitigation Strategy

- All CLI operations are **read-only by default** (require explicit `--write` or confirmation)
- **Dry-run mode** available for all write operations
- Pre-commit hook prevents invalid YAML from entering repository
- Skills use structured CLI calls, not free-form YAML generation
- **PR review required:** Skills should never commit directly to main
- **Commit tagging:** Skill-generated commits should include `[skill:template-registry]` prefix

### Security Invariants

```python
# Every write operation MUST:
1. Validate against schema
2. Check for duplicate IDs
3. Require explicit confirmation (--confirm or interactive)
4. Log the operation with timestamp
5. Never include secrets in templates.yaml
```

## Rollback Procedures

- **Primary mechanism:** `git revert`
- **Makefile target:** `make template-rollback COMMIT=<hash>`
- Skills should never force-push or amend history
- `templates.yaml` changes require PR review (no direct commits to main)

## Testing Strategy

| Type | Description | Location |
|------|-------------|----------|
| **Unit** | Each CLI subcommand with fixtures | `tests/test_template_manager.py` |
| **Integration** | Round-trip tests (add → validate → remove) | `tests/test_template_integration.py` |
| **Skill Testing** | Example interactions | `.claude/skills/template-registry/examples.md` |
| **CI** | Validate templates.yaml on every PR | `.github/workflows/validate.yml` |

## Consequences

### Positive

1. **Reduced errors**: Validation-first prevents malformed entries
2. **Discoverable**: Skills provide context-aware guidance
3. **Flexible**: Multiple interfaces for different workflows
4. **Documented**: Skill instructions serve as documentation
5. **Testable**: Single CLI tool is easily unit tested
6. **Safe**: LLM operations constrained by validation and review

### Negative

1. **Python dependency**: CLI requires Python runtime + ruamel.yaml
2. **Learning curve**: Contributors must understand skill invocation

### Neutral

1. No MCP server overhead (can add later if needed)
2. Direct YAML editing remains possible for power users
3. Schema changes require CLI updates

## Implementation Phases

### Phase 1: Read-Only Foundation

- [ ] Create `scripts/template_manager.py` with `validate` and `list` subcommands
- [ ] Add `ruamel.yaml` to requirements.txt
- [ ] Implement Level 1 + Level 2 validation
- [ ] Create basic Makefile targets (validate, templates, help)
- [ ] Add unit tests for validation logic
- [ ] Update CI to use new validation

**Acceptance Criteria:**
- `make validate` passes on current templates.yaml
- `make templates` outputs formatted list
- Unit tests pass with 90%+ coverage on validation

### Phase 2: Write Operations

- [ ] Implement `add`, `update`, `remove` subcommands
- [ ] Add `--interactive` mode with prompts
- [ ] Add `--dry-run` mode for all write operations
- [ ] Add `--confirm` safety flag for destructive operations
- [ ] Create integration tests (round-trip CRUD)

**Acceptance Criteria:**
- Can add/update/remove templates via CLI
- Dry-run shows accurate preview
- Invalid operations rejected with clear error messages

### Phase 3: Skill Integration

- [ ] Create `.claude/skills/template-registry/SKILL.md`
- [ ] Create `schema-reference.md` from ADR-003
- [ ] Create `examples.md` with common patterns
- [ ] Add pre-commit hook integration
- [ ] Update CONTRIBUTING.md with skill usage

**Acceptance Criteria:**
- Skill triggers correctly on template-related queries
- Claude can successfully add/update templates via skill
- Pre-commit blocks invalid templates

### Phase 4: Polish & Documentation

- [ ] Add Level 3 validation (network checks)
- [ ] Create `docs/TEMPLATE_MANAGEMENT.md` guide
- [ ] Add `make help` documentation
- [ ] Add commit message templates for skill-generated commits

**Acceptance Criteria:**
- Full documentation available
- `make validate-deep` runs network checks
- Contributor guide is complete

## Compliance / Validation

- [ ] CLI loads and runs without errors
- [ ] All validation levels implemented
- [ ] Skill loads correctly in Claude Code
- [ ] Makefile targets work on Linux/macOS
- [ ] Pre-commit hook catches schema violations
- [ ] Security invariants enforced

## Future Considerations

- **MCP Server:** Reconsider at 20+ templates or external API need
- **Template Linting:** Check for common misconfigurations (missing env vars)
- **Template Diff:** Compare template versions across commits
- **Auto-sync:** Fetch template metadata from Railway API (if available)
- **Per-template files:** Consider `templates/<id>.yaml` structure if merge conflicts become frequent

---

## LLM Council Review Summary

**Reviewed:** 2026-01-04
**Tier:** Balanced (4 models: GPT-5.2, Claude Sonnet 4.5, Gemini 3, Grok 4)

### Verdict: Approved with Modifications

Unanimous agreement that the hybrid approach (Skills + Makefile + single Python CLI) is appropriate for current scale.

### Key Findings Incorporated

| Finding | Resolution |
|---------|------------|
| Consolidate Python scripts into single CLI | Implemented `scripts/template_manager.py` with subcommands |
| Use ruamel.yaml to preserve formatting | Added to requirements, documented in decision |
| Add tiered validation (fast/slow) | Three validation levels defined with clear boundaries |
| Security concerns need explicit mitigation | Added Security Considerations section |
| MCP rejection needs criteria | Added threshold: >20 templates OR external API need |
| Missing rollback procedures | Added Rollback Procedures section |
| Testing strategy absent | Added Testing Strategy section |
| Phases need acceptance criteria | Added criteria to each phase |

### Dissenting Views

- All models agreed the hybrid approach is correct for current scale
- Minor disagreement on whether to consider per-template files (deferred to Future Considerations)

---

## References

- [ADR-003: Template Configuration System](ADR-003-template-configuration-system.md)
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [ruamel.yaml Documentation](https://yaml.readthedocs.io/)
- [JSON Schema Validation](https://json-schema.org/)
