# ADR-005: DevSecOps Implementation

**Status:** Accepted 2026-01-03
**Date:** 2026-01-03
**Decision Makers:** @amiable-dev/maintainers
**Depends On:** ADR-004 (CI/CD)
**Council Review:** 2026-01-03 (Tier: High, Models: GPT-5.2, Claude Opus 4.5, Gemini 3 Pro, Grok 4.1)

---

## Context

The amiable-templates project, while primarily a documentation site, requires security measures to:

1. Prevent accidental secret exposure in commits
2. Ensure supply chain security for dependencies
3. Maintain secure CI/CD workflows
4. Support safe contributions from the community (forks)

This ADR adapts the DevSecOps patterns from [llm-council ADR-035](https://github.com/amiable-dev/llm-council/blob/master/docs/adr/ADR-035-devsecops-implementation.md) for a documentation-focused project.

### Current State

The repository has Snyk rules in `.agent/rules/snyk_rules.md` but no automated security scanning.

### Goals

1. Prevent secrets from being committed
2. Keep dependencies up-to-date and secure
3. Maintain fork-friendly CI (no secrets required for PR checks)
4. Minimize false positives and noise

## Non-Goals

- Runtime security (static site has no runtime)
- Container scanning (no containers in this project)
- SAST for application code (minimal Python scripts)
- Full SLSA compliance (overkill for docs site)

## Decision

Implement a **3-layer security pipeline** adapted for documentation projects:

### Layer 1: Pre-Commit (Developer Workstation)

Tools run locally before commits:

| Tool | Purpose |
|------|---------|
| **Gitleaks** | Secret detection |
| **yamllint** | YAML syntax validation |

Configuration: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  - repo: https://github.com/adrienverge/yamllint
    rev: v1.33.0
    hooks:
      - id: yamllint
        args: [--strict]
```

### Layer 2: Pull Request (Fork-Compatible)

Checks that run without secrets (safe for external PRs):

| Tool | Purpose |
|------|---------|
| **Gitleaks Action** | Secret scanning |
| **Dependency Review** | License and vulnerability check |
| **YAML validation** | Configuration syntax |

Workflow: `.github/workflows/security.yml`

```yaml
name: Security

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  dependency-review:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/dependency-review-action@v4
        with:
          fail-on-severity: high
```

### Layer 3: Main Branch (Post-Merge)

Additional checks after merge:

| Tool | Purpose |
|------|---------|
| **Dependabot** | Automated dependency updates |
| **GitHub Secret Scanning** | Native secret detection |

Configuration: `.github/dependabot.yml` (already created in ADR-001)

### Tool Selection Rationale

| Tool | Why Selected |
|------|--------------|
| **Gitleaks** | Fast, configurable, pre-commit + CI support |
| **Dependency Review** | Native GitHub integration, zero config |
| **Dependabot** | Automatic PRs, built into GitHub |
| **yamllint** | Catches YAML errors before they break builds |

### Tools NOT Used (and Why)

| Tool | Reason for Exclusion |
|------|---------------------|
| **CodeQL** | No significant codebase to analyze |
| **Snyk** | Dependabot sufficient for this project size |
| **Trivy** | No containers or complex dependencies |
| **SonarCloud** | Overkill for docs site |
| **Semgrep** | No application code requiring SAST |

### Fork-Friendly Design

All PR checks work without repository secrets:
- Gitleaks uses only `GITHUB_TOKEN` (automatic)
- Dependency Review is token-free
- No external services requiring API keys

### Gitleaks Configuration

`.gitleaks.toml` to reduce false positives (example patterns only):

```toml
[extend]
useDefault = true

# Note: We do NOT globally exclude .md files from scanning.
# Only specific example patterns are allowlisted.

[[rules]]
id = "example-api-key"
description = "Ignore example API keys in documentation"
regex = '''sk-example-[a-zA-Z0-9]+'''
allowlist = { regexes = ['''sk-example-'''] }

[[rules]]
id = "placeholder-key"
description = "Ignore placeholder API keys"
regex = '''YOUR_API_KEY|your-api-key|xxx+'''
allowlist = { regexes = ['''YOUR_API_KEY|your-api-key|xxx+'''] }
```

## Consequences

### Positive

1. **Prevents secret leaks**: Gitleaks catches secrets pre-commit and in CI
2. **Fork-friendly**: External contributors can submit PRs without issues
3. **Low maintenance**: Leverages GitHub-native features
4. **Minimal noise**: Focused toolset avoids alert fatigue

### Negative

1. **Less comprehensive**: Smaller toolset than full DevSecOps
2. **No runtime monitoring**: Static site limitation

### Neutral

1. Security posture appropriate for project risk level
2. Can expand later if project scope grows

## Implementation Phases

### Phase 1: Foundation

- [x] Create `.pre-commit-config.yaml`
- [x] Create `.gitleaks.toml`
- [x] Update `SECURITY.md` with pre-commit instructions

### Phase 2: CI Integration

- [x] Create `.github/workflows/security.yml`
- [x] Enable GitHub Secret Scanning (repository settings)
- [x] Verify Dependabot is active

### Phase 3: Documentation

- [x] Document security setup in CONTRIBUTING.md
- [x] Add security badge to README

## Compliance / Validation

- [x] Pre-commit hooks install and run successfully
- [x] Gitleaks catches test secrets in CI
- [x] Dependency Review blocks vulnerable dependencies
- [x] External PR can pass all checks without secrets

---

## LLM Council Review Summary

**Reviewed:** 2026-01-03
**Tier:** High (4 models: GPT-5.2, Claude Opus 4.5, Gemini 3 Pro, Grok 4.1)

### Verdict: Accepted

Fork-friendly security design is appropriate for community-driven documentation projects.

### Key Findings Incorporated

| Finding | Resolution |
|---------|------------|
| Gitleaks allowlist too broad for `.md` files | Removed global `.md$` exclusion; only specific example patterns allowlisted |
| Consider SBOM generation | Deferred; overkill for docs site with minimal dependencies |
| Pre-commit hook installation friction | Added instructions to CONTRIBUTING.md |
| Link checking for security | Weekly link validation added to prevent malicious link injection |

### Dissenting Views

- All models agreed the 3-layer security approach is appropriate for project scope.
- Minor discussion on whether Snyk should be included; consensus is Dependabot sufficient for this project size.

---

## References

- [llm-council ADR-035: DevSecOps Implementation](https://github.com/amiable-dev/llm-council/blob/master/docs/adr/ADR-035-devsecops-implementation.md)
- [Gitleaks](https://github.com/gitleaks/gitleaks)
- [GitHub Dependency Review](https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-dependency-review)
- [pre-commit](https://pre-commit.com/)
