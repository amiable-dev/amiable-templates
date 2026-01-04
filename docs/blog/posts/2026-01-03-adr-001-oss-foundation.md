---
date: 2026-01-03
authors:
  - amiable-dev
categories:
  - ADRs
  - OSS
tags:
  - adr-001
  - community
  - governance
---

# Building an OSS Foundation: ADR-001 Implementation

How we established community standards for amiable-templates using Architecture Decision Records (ADRs) and multi-model AI review.

<!-- more -->

!!! info "What's an ADR?"
    An Architecture Decision Record documents significant technical decisions with context, options considered, and rationale. It creates a searchable history of *why* things are the way they are.

## The Problem

We're building [amiable-templates](https://github.com/amiable-dev/amiable-templates) to aggregate deployment templates for AI infrastructure into a single portal. Before writing any aggregation code, we needed to answer: *How do we structure an OSS project that invites contribution?*

Starting from scratch means making a lot of decisions:

- What license?
- How do contributors know what's expected?
- How do we handle security reports?
- What governance model fits a small project?

## The Solution: Adopt Proven Patterns

Instead of reinventing the wheel, we borrowed the existing [OSS ADR-033](https://llm-council.dev/adr/ADR-033-oss-community-infrastructure/), which had already been reviewed with the LLM Council and battle-tested for [llm-council.dev](https://llm-council.dev).

### The Files

| File | Purpose |
|------|---------|
| `LICENSE` | MIT - maximum flexibility |
| `CODE_OF_CONDUCT.md` | Contributor Covenant v2.1 |
| `CONTRIBUTING.md` | How to contribute |
| `SECURITY.md` | 48hr target response time |
| `GOVERNANCE.md` | Decision-making process |
| `SUPPORT.md` | Where to get help |

### GitHub Configuration

```
.github/
├── CODEOWNERS           # Auto-assign reviewers
├── dependabot.yml       # Keep deps updated
├── ISSUE_TEMPLATE/      # Structured bug reports
└── PULL_REQUEST_TEMPLATE.md
```

## Example: CODEOWNERS

Here's how we route reviews to the right people:

```text
# Default: maintainers review everything
* @amiable-dev/maintainers

# Critical config requires explicit maintainer approval
templates.yaml @amiable-dev/maintainers
mkdocs.yml @amiable-dev/maintainers

# CI/CD changes are sensitive
.github/ @amiable-dev/maintainers

# ADRs need architectural review
docs/adrs/ @amiable-dev/maintainers
```

This means any PR touching `templates.yaml` (our template registry) automatically requests review from maintainers. As the project grows, we can split ownership - e.g., `docs/ @docs-team`.

## The Interesting Part: LLM Council Review

We used [LLM Council](https://github.com/amiable-dev/llm-council) to review our ADR before accepting it. LLM Council is an MCP server that queries multiple AI models in parallel, has them critique each other's responses, and synthesizes a consensus verdict.

Four models (GPT-5.2, Claude Opus 4.5, Gemini 3 Pro, Grok 4.1) reviewed our draft ADR:

**What they caught:**

| Finding | Our Response |
|---------|--------------|
| Missing CI/CD workflows | Added deploy.yml and security.yml |
| GOVERNANCE.md premature for solo project | Simplified, will expand at 3+ maintainers |
| Need template intake policy | Added to CONTRIBUTING.md |

The full review is documented in [ADR-001](https://github.com/amiable-dev/amiable-templates/blob/main/docs/adrs/ADR-001-project-structure-oss-standards.md#llm-council-review-summary).

## Tracking It All

We used GitHub Issues to track implementation:

- **Epic:** [#5](https://github.com/amiable-dev/amiable-templates/issues/5) - Complete OSS Foundation
- **Sub-issues:** Labels (#6), Branch Protection (#7), Blog (#8), etc.

This gives visibility into what's done and what's remaining.

## What's Next

With the foundation in place, we're moving through the remaining ADRs:

- **ADR-002:** MkDocs site architecture
- **ADR-003:** Template configuration system
- **ADR-004:** CI/CD & deployment
- **ADR-005:** DevSecOps implementation
- **ADR-006:** Cross-project documentation aggregation

Each follows the same process: draft, LLM Council review, implement, document.

---

**Links:**

- [ADR-001: Project Structure & OSS Standards](https://github.com/amiable-dev/amiable-templates/blob/main/docs/adrs/ADR-001-project-structure-oss-standards.md)
- [amiable-templates repository](https://github.com/amiable-dev/amiable-templates)
- [LLM Council](https://github.com/amiable-dev/llm-council)
