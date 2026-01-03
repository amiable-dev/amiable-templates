# ADR-001: Project Structure and OSS Standards

**Status:** Accepted 2026-01-03
**Date:** 2026-01-03
**Decision Makers:** @amiable-dev/maintainers
**Council Review:** 2026-01-03 (Tier: High, Models: GPT-5.2, Claude Opus 4.5, Gemini 3 Pro, Grok 4.1)

---

## Context

The amiable-templates repository is being established as an open source documentation site that aggregates Railway deployment templates from multiple repositories. To maximize community engagement and ensure sustainable maintenance, we need to establish a consistent project structure that:

1. Lowers the barrier to contribution
2. Provides clear governance and communication channels
3. Ensures quality through automated workflows
4. Protects both contributors and maintainers with proper policies
5. Aligns with the amiable-dev organization's existing OSS patterns

### Current State

The repository currently contains:
- `CLAUDE.md` for AI assistant guidance
- `.agent/rules/snyk_rules.md` for security scanning rules

### Goals

1. Establish community standards that encourage contribution
2. Implement governance that scales with community growth
3. Create a consistent experience across amiable-dev repositories
4. Protect the project from common OSS pitfalls (legal, security, maintainer burnout)

## Non-Goals

This ADR explicitly does NOT cover:
- MkDocs site architecture (see ADR-002)
- Template configuration system (see ADR-003)
- CI/CD and deployment (see ADR-004)
- Security scanning implementation (see ADR-005)
- Documentation aggregation (see ADR-006)

## Considered Options

### Option 1: Adopt llm-council OSS Structure (Recommended)

Adopt the proven structure from [llm-council](https://github.com/amiable-dev/llm-council) and [litellm-langfuse-railway](https://github.com/amiable-dev/litellm-langfuse-railway) with adaptations for a documentation site.

**Pros:**
- Consistency across amiable-dev organization
- Proven patterns that have been LLM Council reviewed
- Comprehensive coverage of OSS requirements
- Clear implementation path with existing examples

**Cons:**
- Some overhead for a primarily documentation project
- Initial setup effort

### Option 2: Minimal OSS Structure

Only include LICENSE and README, add other files as needed.

**Pros:**
- Fast initial setup
- Low maintenance overhead

**Cons:**
- Missing professional signals (GitHub Community Profile)
- No contribution guidelines leads to inconsistent PRs
- No security policy delays vulnerability handling
- Must retrofit structure later

## Decision

Adopt the llm-council OSS structure with the following adaptations for this documentation-focused repository:

### 1. Community Standards Files (Root Level)

| File | Purpose | Adaptation |
|------|---------|------------|
| `LICENSE` | MIT License | Standard MIT |
| `CODE_OF_CONDUCT.md` | Contributor Covenant v2.1 | No changes |
| `CONTRIBUTING.md` | Contribution guidelines | Focus on docs contributions, template additions |
| `GOVERNANCE.md` | Decision-making process | Define maintainer roles, ADR process |
| `SECURITY.md` | Vulnerability reporting | Focus on supply chain (dependencies, CI) |
| `SUPPORT.md` | Help channels | GitHub Discussions + issue templates |
| `.gitignore` | Prevent accidental commits | Python/MkDocs patterns, cache directories |
| `.editorconfig` | Consistent formatting | Markdown, YAML, Python settings |

### 2. GitHub Configuration (.github/)

```
.github/
├── CODEOWNERS              # Maintainer review requirements
├── FUNDING.yml             # Sponsorship links
├── dependabot.yml          # Dependency updates (Python, GitHub Actions)
├── ISSUE_TEMPLATE/
│   ├── config.yml          # Template chooser + discussion links
│   ├── bug_report.md       # Site issues, broken links
│   └── feature_request.md  # New template requests
├── PULL_REQUEST_TEMPLATE.md
└── workflows/
    ├── deploy.yml          # Build and deploy to GitHub Pages
    └── security.yml        # Gitleaks secret scanning
```

### 3. CODEOWNERS Configuration

```
# Default owners
* @amiable-dev/maintainers

# Template configuration (critical)
templates.yaml @amiable-dev/maintainers
templates.schema.yaml @amiable-dev/maintainers

# CI/CD workflows
.github/ @amiable-dev/maintainers

# ADRs require review
docs/adrs/ @amiable-dev/maintainers

# Aggregation scripts
scripts/ @amiable-dev/maintainers
```

### 4. Issue Labels

| Label | Description | Color |
|-------|-------------|-------|
| `bug` | Site issues, broken links | #d73a4a |
| `enhancement` | Site improvements | #a2eeef |
| `documentation` | Documentation updates | #0075ca |
| `good-first-issue` | Beginner-friendly | #7057ff |
| `help-wanted` | Needs community help | #008672 |
| `template-request` | Request for new template | #fbca04 |
| `aggregation` | Doc aggregation issues | #c5def5 |
| `upstream` | Issue in source template repo | #e4e669 |

### 5. Versioning Strategy

Use semantic versioning for site releases via Git tags:
- **MAJOR**: Breaking nav structure changes, deprecated pages removed
- **MINOR**: New templates added, new sections
- **PATCH**: Content updates, fixes

### 6. Branch Protection

Enable on `main` branch:
- Require pull request reviews (1 approval)
- Require status checks to pass
- Require signed commits (recommended, not required)
- No force pushes

## Consequences

### Positive

1. **Professional appearance**: GitHub Community Profile shows 100% completion
2. **Lower contribution barrier**: Clear guidelines reduce friction
3. **Consistent governance**: Aligned with other amiable-dev projects
4. **Security posture**: Clear vulnerability reporting process
5. **Discoverability**: Standard files improve SEO

### Negative

1. **Maintenance overhead**: More files to keep updated
2. **Initial setup effort**: One-time cost to create all files
3. **Review burden**: CODEOWNERS requires maintainer approval

### Neutral

1. Documentation site has different needs than code projects
2. Some OSS patterns (DCO, CITATION.cff) may be overkill initially

## Implementation Phases

### Phase 1: Foundation (P0)

- [x] LICENSE (MIT)
- [x] .gitignore (Python/MkDocs patterns)
- [x] .editorconfig
- [x] CODE_OF_CONDUCT.md (Contributor Covenant v2.1)
- [x] SECURITY.md

### Phase 2: Contribution Experience (P0)

- [x] CONTRIBUTING.md
- [x] .github/CODEOWNERS
- [x] .github/ISSUE_TEMPLATE/bug_report.md
- [x] .github/ISSUE_TEMPLATE/feature_request.md
- [x] .github/ISSUE_TEMPLATE/config.yml
- [x] .github/PULL_REQUEST_TEMPLATE.md

### Phase 3: Governance & Sustainability (P1)

- [x] GOVERNANCE.md
- [x] SUPPORT.md
- [x] .github/FUNDING.yml
- [x] .github/dependabot.yml

### Phase 4: GitHub Features (P2)

- [x] Enable GitHub Discussions (Q&A, Ideas, Announcements)
- [x] Configure issue labels
- [x] Enable branch protection rules
- [x] Set repository topics for discoverability

## Compliance / Validation

- [x] All community standards files created and linked from README
- [x] GitHub "Community Standards" checklist shows 100% completion
- [x] Issue templates function correctly (manual test)
- [x] CODEOWNERS properly routes review requests
- [x] Branch protection rules enabled

---

## LLM Council Review Summary

**Reviewed:** 2026-01-03
**Tier:** High (4 models: GPT-5.2, Claude Opus 4.5, Gemini 3 Pro, Grok 4.1)

### Verdict: Accepted with Modifications

The council unanimously agreed that the community health files are robust but identified gaps in technical automation.

### Key Findings Incorporated

| Finding | Resolution |
|---------|------------|
| Missing CI/CD workflows | Added to ADR-004 scope; deploy.yml and security.yml created |
| Missing README.md | Will create during implementation |
| `templates.yaml` validation needed | Added schema validation in CI workflow |
| GOVERNANCE.md may be premature | Kept but simplified; will expand when 3+ maintainers |
| Semantic versioning may be overkill | Changed to continuous deployment; tags for milestones only |
| Link checking for upstream templates | Added to ADR-006 aggregation scope |
| Template intake policy needed | Added to CONTRIBUTING.md |
| Upstream template health monitoring | Added weekly link checking workflow |

### Dissenting Views

- **Claude Opus 4.5**: Suggested deferring GOVERNANCE.md entirely until 3+ contributors. Kept but simplified.
- **GPT-5.2**: Recommended explicit template intake criteria. Added to CONTRIBUTING.md.
- **All models**: Agreed branch protection should only be enabled after CI is working.

---

## References

- [llm-council repository](https://github.com/amiable-dev/llm-council) - Organizational template
- [litellm-langfuse-railway ADR-001](https://github.com/amiable-dev/litellm-langfuse-railway/blob/main/docs/adr/ADR-001-oss-project-structure.md) - Reference implementation
- [GitHub Community Standards](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions)
- [Contributor Covenant](https://www.contributor-covenant.org/)
- [Choose a License](https://choosealicense.com/)
