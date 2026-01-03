# ADR-001 LinkedIn Announcement

---

**We Had AI Review Our Architecture Decisions (Here's What It Caught)**

Before writing code for amiable-templates (a Railway template aggregator), we documented our OSS project structure in an Architecture Decision Record.

Then we did something different: we submitted the draft to LLM Council, which queries 4 AI models, has them critique each other, and synthesizes a verdict.

**What the AI review caught:**

1. Our GOVERNANCE.md was premature - suggested simplifying until we have 3+ contributors
2. We documented structure but forgot to mention CI/CD workflows
3. Missing policy for evaluating new template submissions

All valid points. We fixed them before accepting the ADR.

The full review is documented in the ADR itself, including dissenting views between models.

**The result:** Our OSS foundation is now complete with MIT license, security policy, contribution guidelines, and proper GitHub configuration.

Full ADR with council verdict: https://github.com/amiable-dev/amiable-templates/blob/main/docs/adrs/ADR-001-project-structure-oss-standards.md

Have you tried using AI for architecture or governance reviews? Curious what approaches others have found useful.

#OpenSource #DeveloperExperience #AIInfrastructure #ArchitectureDecisionRecords
