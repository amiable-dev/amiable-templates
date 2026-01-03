# ADR-001 Hacker News Submission

**Title:** Using multi-model AI consensus to review architecture decisions

**URL:** https://github.com/amiable-dev/amiable-templates/blob/main/docs/adrs/ADR-001-project-structure-oss-standards.md

**Note:** Don't use "Show HN" format - this is a text document, not an interactive tool.

---

**Comment:**

We're building amiable-templates, a documentation portal that aggregates Railway deployment templates. Before writing code, we documented our OSS project structure in an Architecture Decision Record.

We submitted the draft to LLM Council, which queries 4 AI models (GPT-5.2, Claude Opus 4.5, Gemini 3 Pro, Grok 4.1), has them critique each other, and synthesizes a verdict.

What the AI review caught:

- Our GOVERNANCE.md was premature for a solo maintainer project - they suggested simplifying until we have 3+ contributors
- We documented the file structure but forgot to reference the actual CI/CD workflows
- Missing policy for how to evaluate new template submissions

All valid catches. The ADR includes the full council review with findings and dissenting views between models.

We're doing this for every architectural decision. Curious if others have experimented with multi-model consensus for architecture review, and what worked or didn't.
