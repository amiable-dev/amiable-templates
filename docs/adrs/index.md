---
title: Architecture Decision Records
---

# Architecture Decision Records (ADRs)

This section contains Architecture Decision Records (ADRs) for the amiable-templates project. ADRs document significant architectural decisions, their context, and consequences.

## What is an ADR?

An Architecture Decision Record captures an important architectural decision along with its context and consequences. We use ADRs to:

- Document why decisions were made
- Provide context for future contributors
- Enable informed decision-making about changes
- Track the evolution of the project

## ADR Process

1. **Draft**: Create an ADR using the [template](ADR-000-template.md)
2. **Review**: Submit for LLM Council review (optional but recommended)
3. **Propose**: Open a PR for community feedback
4. **Accept/Reject**: Core team makes final decision

## Current ADRs

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-000](ADR-000-template.md) | Template | N/A | - |
| [ADR-001](ADR-001-project-structure-oss-standards.md) | Project Structure & OSS Standards | Accepted | 2026-01-03 |
| [ADR-002](ADR-002-mkdocs-site-architecture.md) | MkDocs Site Architecture | Accepted | 2026-01-03 |
| [ADR-003](ADR-003-template-configuration-system.md) | Template Configuration System | Accepted | 2026-01-03 |
| [ADR-004](ADR-004-ci-cd-deployment.md) | CI/CD & Deployment | Accepted | 2026-01-03 |
| [ADR-005](ADR-005-devsecops-implementation.md) | DevSecOps Implementation | Accepted | 2026-01-03 |
| [ADR-006](ADR-006-cross-project-adr-aggregation.md) | Cross-Project Documentation Aggregation | Accepted | 2026-01-03 |

## LLM Council Reviews

ADRs in this project are reviewed by the LLM Council for architectural feedback. The council provides:

- Multi-model perspectives on design decisions
- Identification of risks and gaps
- Suggestions for alternatives
- Consensus-driven recommendations

Council review tiers:
- **Quick**: 2 models, ~10 seconds
- **Balanced**: 3 models, ~25 seconds
- **High**: Full council, ~45 seconds
