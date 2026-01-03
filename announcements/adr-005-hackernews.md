# ADR-005 Hacker News Announcement

**Title:** Fork-Safe DevSecOps: Solving the OSS Secret Constraint

**URL:** https://amiable-dev.github.io/amiable-templates/blog/2026/01/03/devsecops-for-a-docs-site-adr-005/

**Comment to post with submission:**

We set up security scanning for a documentation repository. The constraint that shaped everything: fork PRs can't access repository secrets.

If your security workflow requires SONAR_TOKEN or SNYK_TOKEN, every community contribution fails CI. Contributors wait for maintainers to approve, friction accumulates.

Our approach: Separate validation (runs on untrusted fork PRs) from deployment (runs post-merge in trusted context). PR validation uses only GITHUB_TOKEN (automatically provided to forks).

The pipeline:
- PR Validation (untrusted): Gitleaks Action + Dependency Review
- Post-Merge (trusted): Dependabot + Secret Scanning + Deployment

The interesting failure: We initially allowlisted all `.md` files from Gitleaks scanning. For a docs repo, that's most of the codebase—and exactly where secrets leak (tutorial code blocks with accidentally-pasted API keys).

The other failure: yamllint parsing `on:` in GitHub Actions workflows. YAML 1.1 treats `on`, `off`, `yes`, `no` as booleans (The Norway Problem—country code NO becomes false). This breaks in linters that use PyYAML, not in the GitHub Actions parser itself.

Source: https://github.com/amiable-dev/amiable-templates
