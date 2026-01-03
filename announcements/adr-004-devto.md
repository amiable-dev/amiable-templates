# ADR-004 Dev.to Announcement

**Title:** Why We Chose GitHub Pages Over Netlify (It's Not About Cost)

**Tags:** github, devops, cicd, documentation, webdev

---

Everyone says "GitHub Pages is free." So is Netlify. So is Vercel. Cost isn't the differentiator.

Here's why we chose GitHub Pages for our documentation site:

## The Real Reasons

### 1. Vendor Consolidation

With GitHub Pages:
- Secrets stay in GitHub
- Permissions managed in one place
- Logs in one dashboard

With Netlify/Vercel:
- OAuth connection to configure
- Separate secrets management
- Another dashboard to monitor

### 2. Fewer Security Surface Areas

Every integration is a potential vulnerability. GitHub Pages uses GitHub's built-in OIDC—no API keys to rotate.

### 3. Workflow Simplicity

```yaml
- uses: actions/deploy-pages@v4
```

That's it. The action handles the artifact upload and deployment.

## The Trade-Off

**No PR preview deployments.**

Netlify and Vercel generate unique URLs for every PR. GitHub Pages doesn't.

For a React app with visual changes, that's painful. For documentation where changes are markdown diffs, we can live without it.

## The yamllint Surprise

Our first security run failed:

```
##[warning] .github/workflows/deploy.yml:3:1 [truthy] truthy value should be one of [false, true]
```

GitHub Actions uses `on:` as a keyword. yamllint sees it as a truthy value (like `yes` or `on` in YAML).

The fix:

```yaml
# .yamllint.yml
rules:
  truthy:
    allowed-values: ['true', 'false', 'on']
```

Lesson: Linting tools need per-ecosystem configuration.

## The Pipeline

```
Push to main → Validate → Cache → Aggregate → Build → Deploy
     ↓
  Security (parallel) → Gitleaks, yamllint
```

Security runs in parallel. A lint failure doesn't block deployment—but shows up as a failed check.

Full ADR with diagrams: https://amiable-dev.github.io/amiable-templates/blog/2026/01/03/cicd-for-a-docs-site-adr-004/
