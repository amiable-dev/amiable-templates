# ADR-005 Twitter Announcement

Just shipped a fork-safe security pipeline for our OSS docs.

The constraint: fork PRs can't access secrets.
The fix: 3-layer pipeline using only GITHUB_TOKEN for PR validation.

Gotcha: Don't allowlist `.md` files in Gitleaks. Docs are where API keys leak.

https://amiable-dev.github.io/amiable-templates/blog/2026/01/03/devsecops-for-a-docs-site-adr-005/

#DevSecOps #OpenSource #GitHubActions
