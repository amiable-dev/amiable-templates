# ADR-002: MkDocs Site Architecture

**Status:** Accepted 2026-01-03
**Date:** 2026-01-03
**Decision Makers:** @amiable-dev/maintainers
**Depends On:** ADR-001 (Project Structure)
**Council Review:** 2026-01-03 (Tier: Balanced, Models: GPT-5.2, Claude Opus 4.5, Gemini 3 Pro, Grok 4.1)

---

## Context

The amiable-templates project requires a documentation site to aggregate and present Railway deployment templates. The site must:

1. Showcase available templates in an attractive, scannable format
2. Aggregate documentation from multiple source repositories
3. Provide excellent search and navigation
4. Support dark/light mode for accessibility
5. Be easy to maintain and contribute to

### Current State

No documentation site exists. Templates are documented in individual repositories.

### Goals

1. Unified documentation portal for all amiable-dev templates
2. Quick Start guide prominently featured
3. Template grid with filtering/categorization
4. Searchable across all aggregated content
5. Mobile-responsive design

## Non-Goals

- Complex JavaScript interactivity (static site preferred)
- User authentication
- Comments/discussion on pages (use GitHub Discussions)
- Real-time content updates (build-time aggregation is sufficient)

## Considered Options

### Option 1: MkDocs Material (Recommended)

Use MkDocs with the Material theme, consistent with llm-council documentation.

**Pros:**
- Excellent search (lunr.js based)
- Beautiful, professional design
- Dark/light mode built-in
- Active development and community
- Markdown-based, easy to contribute
- Python ecosystem (aligns with aggregation scripts)
- Proven pattern in amiable-dev organization

**Cons:**
- Less flexible than custom solutions
- Plugin ecosystem smaller than some alternatives

### Option 2: Docusaurus

React-based documentation framework from Meta.

**Pros:**
- Powerful plugin system
- React components for interactivity
- Good search with Algolia integration

**Cons:**
- Different stack from other amiable-dev projects
- Heavier build process
- More complex for simple docs

### Option 3: Custom Next.js/Astro Site

Build a custom documentation site.

**Pros:**
- Full control over design and features
- Could include advanced interactivity

**Cons:**
- Significant development effort
- Ongoing maintenance burden
- Overkill for documentation needs

## Decision

Use **MkDocs Material** for the documentation site with the following architecture:

### 1. Site Structure

```
docs/
├── index.md                    # Home page with hero + template grid preview
├── quickstart.md               # Quick Start guide (top-level, prominent)
├── templates/
│   ├── index.md                # Full template grid
│   └── {template-id}/          # Aggregated template docs
│       ├── overview.md
│       └── ...
├── adrs/
│   ├── index.md                # ADR index
│   ├── ADR-000-template.md
│   └── aggregated/             # ADRs from template repos
├── blog/                       # Future: announcements
├── contributing.md
├── tags.md
├── img/
└── stylesheets/
    └── extra.css
```

### 2. Navigation Structure

**Top Tabs:**
- Home
- Quick Start
- Templates
- ADRs
- Contributing

**Templates Section Sidebar:**
- Template Grid (index)
- Category groupings
- Individual template docs

### 3. Theme Configuration

```yaml
theme:
  name: material
  palette:
    - scheme: default (light)
    - scheme: slate (dark)
  features:
    - navigation.instant
    - navigation.tabs
    - navigation.sections
    - navigation.top
    - search.suggest
    - search.highlight
    - content.code.copy
```

### 4. Template Grid Design

Use CSS Grid with cards showing:
- Template name and description
- Key features (bulleted)
- Deploy button (Railway)
- GitHub link
- Estimated monthly cost

Implemented as static Markdown with custom CSS, avoiding JavaScript complexity.

### 5. Plugins

| Plugin | Purpose |
|--------|---------|
| `search` | Full-text search |
| `tags` | Categorization and filtering |

### 6. Extensions

| Extension | Purpose |
|-----------|---------|
| `admonition` | Notes, warnings, tips |
| `superfences` | Code blocks, Mermaid diagrams |
| `tabbed` | Code examples in multiple languages |
| `toc` | Table of contents with permalinks |

## Consequences

### Positive

1. **Consistent with organization**: Same stack as llm-council docs
2. **Easy contributions**: Markdown-based, low barrier
3. **Great UX**: Material theme is polished and accessible
4. **Fast builds**: Static site generation is quick
5. **SEO-friendly**: Static HTML, proper meta tags

### Negative

1. **Limited interactivity**: No client-side filtering without JavaScript
2. **Build-time content**: Changes require rebuild/redeploy

### Neutral

1. Template grid is static but sufficient for current scale
2. Search is client-side (lunr.js), not server-side

## Implementation Phases

### Phase 1: Foundation

- [ ] mkdocs.yml configuration
- [ ] requirements.txt with dependencies
- [ ] Home page with hero section
- [ ] Quick Start page
- [ ] Basic template grid

### Phase 2: Styling

- [ ] Custom CSS for hero section
- [ ] Template card styling
- [ ] Dark mode verification
- [ ] Mobile responsiveness testing

### Phase 3: Content

- [ ] ADR section structure
- [ ] Contributing page
- [ ] Tags configuration

## Compliance / Validation

- [ ] Site builds without errors (`mkdocs build --strict`)
- [ ] All internal links valid
- [ ] Mobile responsive (test on various screen sizes)
- [ ] Dark mode functions correctly
- [ ] Search returns relevant results

---

## LLM Council Review Summary

**Reviewed:** 2026-01-03
**Tier:** Balanced (4 models: GPT-5.2, Claude Opus 4.5, Gemini 3 Pro, Grok 4.1)

### Verdict: Accepted

Strong alignment with configuration (ADR-003) and deployment (ADR-004) decisions.

### Key Findings Incorporated

| Finding | Resolution |
|---------|------------|
| "Glue" gap between YAML config and grid | Aggregation script (ADR-006) generates template docs; grid uses static markdown with manual updates initially |
| Need for generator script | `scripts/aggregate_templates.py` handles content transformation |
| Fallback experience for upstream failures | Display "View on GitHub" link when content unavailable |

### Dissenting Views

- All models agreed the architecture is coherent and well-suited for the use case.

---

## References

- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
- [llm-council documentation](https://github.com/amiable-dev/llm-council)
- [ADR-033: OSS Community Infrastructure](https://github.com/amiable-dev/llm-council/blob/master/docs/adr/ADR-033-oss-community-infrastructure.md)
