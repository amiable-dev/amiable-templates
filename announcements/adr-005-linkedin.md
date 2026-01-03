# ADR-005 LinkedIn Announcement

Last week, a contributor's PR sat failing for 3 days. The reason? Our security workflow needed SONAR_TOKEN. Fork PRs can't access repository secrets.

This is the hidden tax on OSS maintenance: security tooling that blocks community contributions.

**The root cause:**

GitHub intentionally isolates secrets from fork PRs to prevent malicious code from exfiltrating credentials. Good security, but it breaks workflows that depend on external services.

**What we built: Fork-Safe DevSecOps**

Our security pipeline separates validation (runs on all PRs, untrusted) from deployment (runs post-merge, trusted):

- **PR Checks:** Gitleaks + Dependency Review using only GITHUB_TOKEN
- **Post-Merge:** Dependabot + Secret Scanning

Result: Contributors' PRs pass CI immediately. No waiting for maintainer approval.

**The gotcha that almost burned us:**

We initially allowlisted all `.md` files from Gitleaks. For a docs repo, that's most of the codebase—and exactly where secrets leak. Tutorial code blocks with accidentally-pasted API keys.

**The fix:** Allowlist specific patterns (`sk-example-*`), not entire file types.

Full write-up with code examples: https://amiable-dev.github.io/amiable-templates/blog/2026/01/03/devsecops-for-a-docs-site-adr-005/

How do you handle security scanning for community-driven repos?
