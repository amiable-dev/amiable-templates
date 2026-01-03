# ADR-004 Hacker News Announcement

**Title:** ADR: Moving docs CI/CD to GitHub Actions (trade-offs + YAML 1.1 gotcha)

**URL:** https://amiable-dev.github.io/amiable-templates/blog/2026/01/03/cicd-for-a-docs-site-adr-004/

**Comment to post with submission:**

We consolidated our documentation site's CI/CD to GitHub Pages + Actions. The goal was reducing integration seams—fewer dashboards, fewer permission models, fewer places to check when things break.

Stack before: GitHub (code) + Netlify (deploy) + separate secrets management
Stack after: GitHub handles everything

Trade-off accepted: No PR preview deployments. For docs where changes are markdown diffs, reviewing in GitHub is sufficient. For a frontend app with visual components, we'd reconsider.

The interesting failure: yamllint treats `on:` as a YAML 1.1 boolean. In YAML 1.1, `on`, `off`, `yes`, `no` are all booleans. GitHub Actions uses `on:` as a keyword.

```
[truthy] truthy value should be one of [false, true]
```

Fix: Configure yamllint to allow `on` as a truthy value, or quote the key (`'on':`).

Source: https://github.com/amiable-dev/amiable-templates
