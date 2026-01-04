---
date: 2026-01-03
authors:
  - amiable-dev
categories:
  - ADRs
  - Architecture
tags:
  - adr-002
  - mkdocs
  - material-theme
---

# Choosing MkDocs Material: ADR-002 Site Architecture

Why we chose MkDocs Material over Docusaurus or a custom solution, and how we structured the site.

<!-- more -->

## The Problem

We needed a documentation site that could showcase templates in a scannable, attractive format. The site also needed to aggregate documentation from multiple template repositories, provide excellent search, support dark/light mode for accessibility, and be easy for contributors to work with.

Three options emerged: MkDocs Material, Docusaurus, or a custom Next.js/Astro site.

## Why MkDocs Material?

| Criteria | MkDocs Material | Docusaurus | Custom |
|----------|----------------|------------|--------|
| Stack alignment | Python (matches scripts) | React/Node | Varies |
| Setup time | Hours | Hours | Days/Weeks |
| Maintenance | Low | Medium | High |
| Search | Built-in (lunr.js) | Algolia needed | Build it |
| Dark mode | Built-in | Built-in | Build it |

**Why not Docusaurus?** It's a great framework, and we use it in our own blog [amiable.dev](https://amiable.dev) but it would introduce React/Node into a Python-focused project. Our aggregation scripts are Python, and having a consistent stack reduces cognitive load.

**Why not custom?** A Next.js or Astro site would give us full control, but it's overkill for documentation. We'd spend weeks building what MkDocs Material gives us out of the box.

The deciding factor: **consistency**. Our [llm-council](https://github.com/amiable-dev/llm-council) docs already use MkDocs Material. Same tooling, same patterns, same contributor experience.

## The Architecture

```
docs/
├── index.md          # Hero + featured templates
├── quickstart.md     # Prominent, top-level
├── templates/        # Template grid + aggregated docs
├── adrs/             # Architecture decisions
├── blog/             # You're reading it
└── stylesheets/
    └── extra.css     # Hero + grid styling
```

### Navigation Tabs

We use top-level tabs for main sections:

```yaml
nav:
  - Home: index.md
  - Quick Start: quickstart.md
  - Templates: templates/index.md
  - ADRs: adrs/index.md
  - Contributing: contributing.md
  - Blog: blog/index.md
```

Quick Start gets its own tab because that's what most visitors want.

## The Template Grid

We wanted a scannable grid of template cards without any JavaScript complexity. Here's how we built it using pure markdown with custom CSS:

```markdown
<div class="template-grid" markdown="1">

<div class="template-card" markdown="1">

### LiteLLM + Langfuse Starter

Production-ready LLM proxy with observability.

**Features:**
- 100+ LLM providers via LiteLLM
- Request tracing with Langfuse
- Cost tracking and analytics

**Estimated Cost:** ~$29-68/month

[:octicons-rocket-16: Deploy](https://railway.app/template/...)
[:octicons-mark-github-16: Source](https://github.com/amiable-dev/litellm-langfuse-railway)

</div>

<div class="template-card" markdown="1">

### Another Template

Description here...

</div>

</div>
```

The `markdown` attribute is key—it tells MkDocs Material to process the markdown inside the HTML divs.

The CSS does the heavy lifting:

```css
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
}

.template-card {
  border: 1px solid var(--md-default-fg-color--lightest);
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.template-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}
```

No framework needed. Pure CSS grid with markdown content.

## Dark Mode

MkDocs Material handles dark mode elegantly with palette configuration. Users get automatic detection based on their system preference, plus a toggle to override:

```yaml
theme:
  name: material
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: deep purple
      accent: deep purple
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: deep purple
      accent: deep purple
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
```

The toggle icon appears in the header. No JavaScript to write, no state to manage—it just works.

## What We Learned

1. **Start with constraints**: "No JavaScript" forced simpler, more maintainable solutions
2. **Reuse organizational patterns**: Same theme as llm-council = less cognitive load
3. **Put Quick Start first**: Most visitors want to deploy, not read architecture docs

## What's Next

- **ADR-003**: Template configuration system (templates.yaml)
- **ADR-006**: Cross-project documentation aggregation

---

**Links:**

- [ADR-002: MkDocs Site Architecture](https://github.com/amiable-dev/amiable-templates/blob/main/docs/adrs/ADR-002-mkdocs-site-architecture.md)
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
- [Live site](https://amiable-dev.github.io/amiable-templates/)
