# ADR-004: CI/CD and Deployment

**Status:** Accepted 2026-01-03
**Date:** 2026-01-03
**Decision Makers:** @amiable-dev/maintainers
**Depends On:** ADR-002 (Site Architecture), ADR-003 (Configuration)
**Council Review:** 2026-01-03 (Tier: Balanced, Models: GPT-5.2, Claude Opus 4.5, Gemini 3 Pro, Grok 4.1)

---

## Context

The amiable-templates documentation site requires a CI/CD pipeline to:

1. Validate configuration and content on pull requests
2. Build and deploy the site to a public URL
3. Aggregate documentation from template repositories
4. Refresh content periodically to catch upstream changes

### Current State

No CI/CD pipeline exists. The repository has no deployment configuration.

### Goals

1. Automated deployment on merge to main
2. Preview deployments for PRs (optional)
3. Scheduled rebuilds to catch upstream doc changes
4. Fast builds with intelligent caching
5. Security-conscious workflow design

## Non-Goals

- Custom deployment infrastructure
- Multiple environment deployments (staging/production)
- A/B testing or gradual rollouts

## Considered Options

### Option 1: GitHub Pages (Recommended)

Deploy to GitHub Pages using GitHub Actions.

**Pros:**
- Free for public repositories
- Native GitHub integration
- Simple configuration
- Reliable CDN
- Custom domain support
- HTTPS by default

**Cons:**
- Limited to static content
- No server-side features

### Option 2: Netlify/Vercel

Deploy to a dedicated static site host.

**Pros:**
- Preview deployments per PR
- Advanced CDN features
- Serverless functions available

**Cons:**
- Additional service to manage
- May have usage limits
- External dependency

### Option 3: Railway

Deploy on Railway, consistent with templates.

**Pros:**
- Consistent platform
- Easy Docker deployment

**Cons:**
- Cost for always-on service
- Overkill for static site

## Decision

Use **GitHub Pages** with GitHub Actions for deployment:

### 1. Workflow: `.github/workflows/deploy.yml`

```yaml
name: Deploy Documentation

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
  workflow_dispatch:
    inputs:
      force_refresh:
        description: 'Force refresh all cached content'
        type: boolean
        default: false

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Restore cache
        uses: actions/cache@v4
        with:
          path: .cache/templates
          key: templates-${{ hashFiles('templates.yaml') }}-${{ github.run_id }}
          restore-keys: |
            templates-${{ hashFiles('templates.yaml') }}-
            templates-

      - name: Aggregate template docs
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python scripts/aggregate_templates.py

      - name: Build MkDocs
        run: mkdocs build --strict

      - uses: actions/upload-pages-artifact@v3
        with:
          path: site/

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/deploy-pages@v4
        id: deployment
```

### 2. Build Triggers

| Trigger | Purpose |
|---------|---------|
| `push: main` | Deploy on merge |
| `schedule: daily` | Refresh upstream content |
| `workflow_dispatch` | Manual rebuild with force refresh option |

### 3. Caching Strategy

- **Template cache**: Commit SHA-based invalidation
- **Python dependencies**: Cached by pip
- **Actions cache**: Restored across runs

Expected build times:
- Cold build: 30-60 seconds
- Cached build: 15-30 seconds

### 4. Security Considerations

- `GITHUB_TOKEN`: Built-in, minimal permissions
- `permissions`: Explicitly declared (least privilege)
- No external secrets required for public repos
- SHA-pinned actions (supply chain security)

### 5. Workflow: `.github/workflows/security.yml`

Separate security scanning workflow:

```yaml
name: Security

on: [push, pull_request]

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
```

### 6. Branch Protection

Configure on `main`:
- Require status checks: `build`, `gitleaks`
- Require PR review (1 approval)
- No force pushes

## Consequences

### Positive

1. **Free hosting**: GitHub Pages is free for public repos
2. **Native integration**: No external services to manage
3. **Automatic HTTPS**: SSL certificates handled
4. **Daily refresh**: Catches upstream changes

### Negative

1. **No PR previews**: Would need Netlify/Vercel for this
2. **Build limits**: GitHub Actions has usage limits (generous for public repos)

### Neutral

1. Custom domain requires DNS configuration
2. Build logs visible in Actions tab

## Implementation Phases

### Phase 1: Basic Pipeline

- [ ] Create deploy.yml workflow
- [ ] Configure GitHub Pages in repository settings
- [ ] Verify deployment works

### Phase 2: Caching

- [ ] Implement template caching
- [ ] Optimize build times
- [ ] Add cache invalidation logic

### Phase 3: Security

- [ ] Create security.yml workflow
- [ ] Configure branch protection
- [ ] Enable Dependabot

### Phase 4: Scheduled Builds

- [ ] Enable daily scheduled builds
- [ ] Add manual trigger with force refresh
- [ ] Monitor for failures

## Compliance / Validation

- [ ] Site deploys successfully on merge
- [ ] Scheduled builds run daily
- [ ] Manual dispatch works with force refresh
- [ ] Security checks pass on PRs
- [ ] Branch protection rules enforced

---

## LLM Council Review Summary

**Reviewed:** 2026-01-03
**Tier:** Balanced (4 models: GPT-5.2, Claude Opus 4.5, Gemini 3 Pro, Grok 4.1)

### Verdict: Accepted

SHA-based caching strategy demonstrates consistent focus on build efficiency.

### Key Findings Incorporated

| Finding | Resolution |
|---------|------------|
| API rate limiting concern (60/hr unauthenticated) | Use automatic `GITHUB_TOKEN` (1000/hr) in GitHub Actions |
| Freshness lag between daily runs | Acceptable trade-off; manual dispatch available for urgent updates |
| Need for link checking | Added weekly link validation consideration |

### Dissenting Views

- All models agreed GitHub Pages is the appropriate deployment target for this project.

---

## References

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions for Pages](https://github.com/actions/deploy-pages)
- [MkDocs GitHub Pages deployment](https://www.mkdocs.org/user-guide/deploying-your-docs/)
