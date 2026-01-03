# ADR-002 LinkedIn Announcement

Constraints lead to simpler architecture.

We needed a documentation site for Railway deployment templates. Three options: MkDocs Material, Docusaurus, or custom.

We chose MkDocs Material. Here's why:

**Stack alignment matters.** Our aggregation scripts are Python. Adding React/Node for docs would split the codebase and increase cognitive load.

**Organizational consistency wins.** Our llm-council project already uses MkDocs Material. Same patterns, same contributor experience across repositories.

**CSS Grid beats build complexity.** We built a template grid using pure markdown with custom CSS. No React components, no build pipeline changes—just markdown with the `markdown="1"` attribute to enable nested content.

The key insight: "No custom JavaScript" as a constraint forced us toward more maintainable patterns.

Read the full ADR with code examples: https://amiable-dev.github.io/amiable-templates/blog/2026/01/03/choosing-mkdocs-material-adr-002-site-architecture/

What's your go-to stack for documentation sites?
