# ADR-004 LinkedIn Announcement

We killed PR preview deployments. Here's why.

Our documentation site now deploys exclusively through GitHub Pages + Actions. We evaluated Netlify and Vercel—both have free tiers, both offer PR previews. We chose GitHub anyway.

**The reasoning: Reduce integration seams**

Before: GitHub (code) + Netlify (deploy) + Cloudflare (DNS) = 3 dashboards, 3 permission models, 3 places to check when things break.

After: GitHub handles code, CI, and hosting. Secrets in one place. Logs in one place.

**The trade-off we accepted:**

No ephemeral PR environments. For a React app with visual components, that would hurt. For documentation where PRs are markdown diffs, reviewing in GitHub is sufficient.

**The humbling lesson:**

Our yamllint workflow failed immediately:

```
[truthy] truthy value should be one of [false, true]
```

GitHub Actions uses `on:` as a trigger keyword. But YAML 1.1 treats `on` as a boolean (like `yes` and `off`). yamllint followed the old spec.

Fix: `.yamllint.yml` with `truthy: { allowed-values: ['true', 'false', 'on'] }`

Full write-up: https://amiable-dev.github.io/amiable-templates/blog/2026/01/03/cicd-for-a-docs-site-adr-004/

Do you quote your YAML keys or tune your linter?
