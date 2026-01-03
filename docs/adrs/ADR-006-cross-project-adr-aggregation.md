# ADR-006: Cross-Project Documentation Aggregation

**Status:** Accepted 2026-01-03
**Date:** 2026-01-03
**Decision Makers:** @amiable-dev/maintainers
**Depends On:** ADR-003 (Configuration), ADR-004 (CI/CD)
**Council Review:** 2026-01-03 (Tier: High, Models: GPT-5.2, Claude Opus 4.5, Gemini 3 Pro, Grok 4.1)

---

## Context

The amiable-templates site aggregates documentation from multiple template repositories. Each template repository contains its own documentation that should be pulled into the unified site. We need a system that:

1. Fetches documentation from configured repositories at build time
2. Transforms content for the unified site context
3. Handles caching efficiently for fast builds
4. Gracefully handles missing or changed content

This ADR adapts patterns from [amiable-docusaurus ADR-003: Cross-Project ADR Aggregation](https://amiable.dev/docs/adrs/ADR-003-cross-project-adr-aggregation).

### Current State

No aggregation system exists. Template documentation is manually referenced via links.

### Goals

1. Automated fetching of template documentation at build time
2. Consistent presentation across all template docs
3. Source attribution for aggregated content
4. Fast incremental builds via caching
5. Resilient to upstream changes

## Non-Goals

- Real-time synchronization (build-time is sufficient)
- Editing aggregated content in this repository
- Version history of aggregated content
- Webhook-triggered updates

## Decision

Implement **build-time documentation aggregation** using Python scripts:

### 1. Aggregation Script: `scripts/aggregate_templates.py`

```python
#!/usr/bin/env python3
"""
Fetch documentation from template repositories at build time.
Reads configuration from templates.yaml.
"""

import asyncio
import json
import os
import re
from pathlib import Path
from datetime import datetime

import aiohttp
import yaml

GITHUB_RAW_BASE = "https://raw.githubusercontent.com"
GITHUB_API_BASE = "https://api.github.com"

class TemplateAggregator:
    def __init__(self, config_path: str = "templates.yaml"):
        self.config = self._load_config(config_path)
        self.cache_dir = Path(".cache/templates")
        self.output_dir = Path("docs/templates")
        self.token = os.environ.get("GITHUB_TOKEN")

    async def aggregate_all(self):
        """Fetch docs from all configured templates."""
        async with aiohttp.ClientSession() as session:
            for template in self.config.get("templates", []):
                await self.aggregate_template(session, template)

    async def aggregate_template(self, session, template):
        """Fetch and transform docs for a single template."""
        template_id = template["id"]
        owner = template["repo"]["owner"]
        repo = template["repo"]["name"]

        # Get current commit SHA
        sha = await self._get_commit_sha(session, owner, repo)
        if not sha:
            print(f"  Warning: Could not fetch SHA for {owner}/{repo}")
            return

        # Check cache
        if self._is_cached(template_id, sha):
            print(f"  Using cached content for {template_id}")
            return

        # Fetch each doc
        output_path = self.output_dir / template_id
        output_path.mkdir(parents=True, exist_ok=True)

        for doc in template["directories"]["docs"]:
            content = await self._fetch_file(
                session, owner, repo, sha, doc["path"]
            )
            if content:
                transformed = self._transform_content(
                    content, owner, repo, sha, doc["path"]
                )
                target = output_path / doc["target"]
                target.write_text(transformed)
                print(f"  Wrote {doc['target']}")

        self._update_cache(template_id, sha)

    def _transform_content(self, content, owner, repo, sha, path):
        """Transform content for unified site."""
        # Rewrite relative links to absolute GitHub URLs
        content = self._rewrite_links(content, owner, repo, sha, path)

        # Inject source attribution
        source_url = f"https://github.com/{owner}/{repo}/blob/{sha}/{path}"
        attribution = f"""
!!! info "Source"
    This documentation is from [{owner}/{repo}]({source_url}).
    Last synced: {datetime.utcnow().strftime('%Y-%m-%d')}

"""
        return attribution + content

    def _rewrite_links(self, content, owner, repo, sha, path):
        """Rewrite relative links to absolute GitHub URLs."""
        base_path = Path(path).parent

        # Rewrite images
        def replace_image(match):
            alt, src = match.groups()
            if src.startswith(('http://', 'https://')):
                return match.group(0)
            resolved = (base_path / src).as_posix()
            return f"![{alt}]({GITHUB_RAW_BASE}/{owner}/{repo}/{sha}/{resolved})"

        content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, content)
        return content
```

### 2. Caching Strategy

Cache structure:
```
.cache/templates/
├── manifest.json     # Tracks commit SHAs
└── raw/              # Cached raw content
    └── {template-id}/
```

Manifest format:
```json
{
  "litellm-langfuse-starter": {
    "commit_sha": "abc123...",
    "fetched_at": "2026-01-03T10:00:00Z",
    "files": ["overview.md", "setup.md"]
  }
}
```

Cache invalidation:
- Compare current commit SHA with cached SHA
- If different, refetch all docs for that template
- Daily scheduled builds ensure freshness

### 3. Content Transformation

| Transformation | Purpose |
|----------------|---------|
| **Link rewriting** | Relative → absolute GitHub URLs |
| **Image rewriting** | Point to raw.githubusercontent.com |
| **Source attribution** | Add info box with source link |
| **Front matter** | Inject MkDocs metadata |

### 4. Error Handling

| Scenario | Behavior |
|----------|----------|
| Template repo not found | Skip, log warning |
| Doc file not found | Skip file, continue others |
| Rate limit hit | Use cached content, warn |
| API error | Use cached content if available |

**Never fail the build** due to upstream issues.

### 5. GitHub API Usage

- Authenticated via `GITHUB_TOKEN` (5000 req/hr)
- Use raw.githubusercontent.com for content (no rate limit)
- Use Trees API for efficient directory listing
- Cache reduces API calls significantly

### 6. Integration with CI

In `.github/workflows/deploy.yml`:

```yaml
- name: Aggregate template docs
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: python scripts/aggregate_templates.py

- name: Build MkDocs
  run: mkdocs build --strict
```

### 7. ADR Aggregation

ADRs are fetched similarly:
- Read from `docs/adr/` in each template repo
- Write to `docs/adrs/aggregated/{template-id}/`
- Include in navigation under ADRs section

## Consequences

### Positive

1. **Unified experience**: All template docs in one place
2. **Always fresh**: Daily rebuilds catch upstream changes
3. **Fast builds**: Caching minimizes fetch time
4. **Resilient**: Cached content used on errors

### Negative

1. **Build dependency**: Requires GitHub API access
2. **Delayed updates**: Changes not instant (daily rebuild)
3. **Complexity**: Aggregation script to maintain

### Neutral

1. Content transformation may need updates for edge cases
2. Large template repos may slow initial builds

## Implementation Phases

### Phase 1: Core Aggregation

- [x] Create `scripts/aggregate_templates.py`
- [x] Implement basic fetch and cache
- [x] Test with litellm-langfuse-railway

### Phase 2: Transformation

- [x] Implement link rewriting
- [x] Add source attribution
- [x] Handle front matter

### Phase 3: Integration

- [x] Add to CI workflow
- [x] Configure caching in GitHub Actions
- [x] Test scheduled builds

### Phase 4: ADR Aggregation

- [ ] Extend script for ADRs (deferred - templates may not have ADRs)
- [x] Update navigation
- [ ] Generate ADR index (deferred)

## Compliance / Validation

- [x] Aggregation completes without errors
- [x] Links in aggregated content work
- [x] Images display correctly
- [x] Cache speeds up subsequent builds
- [x] Errors don't fail the build

---

## LLM Council Review Summary

**Reviewed:** 2026-01-03
**Tier:** High (4 models: GPT-5.2, Claude Opus 4.5, Gemini 3 Pro, Grok 4.1)

### Verdict: Accepted

Robust aggregation design with appropriate caching and error handling strategies.

### Key Findings Incorporated

| Finding | Resolution |
|---------|------------|
| Rate limiting concern (60/hr unauthenticated) | Use `GITHUB_TOKEN` in CI (5000/hr authenticated) |
| Link validation for aggregated content | Added link checking to weekly schedule |
| Large file handling | Added size limit check (>1MB files logged and skipped) |
| Attribution injection placement | Info box at top of content for visibility |

### Dissenting Views

- All models agreed build-time aggregation is appropriate for this use case.
- Discussion on caching granularity (file vs. template level); consensus on template-level for simplicity.

---

## References

- [amiable-docusaurus ADR-003: Cross-Project ADR Aggregation](https://amiable.dev/docs/adrs/ADR-003-cross-project-adr-aggregation)
- [GitHub REST API](https://docs.github.com/en/rest)
- [aiohttp](https://docs.aiohttp.org/)
