# ADR-005 Dev.to Announcement

**Title:** Fork-Safe DevSecOps: Security Scanning Without Breaking Community PRs

**Tags:** security, devops, github, opensource, cicd

---

Most DevSecOps guides assume you have application code to scan. Documentation repositories don't. But they still need security—build-time secrets leak, dependencies have vulnerabilities, and markdown files often contain accidentally-pasted API keys.

Here's how we set up security scanning that works for community contributions.

## The Fork Problem

GitHub intentionally isolates repository secrets from fork PRs (to prevent malicious PRs from exfiltrating credentials). If your security workflow uses `SONAR_TOKEN` or `SNYK_TOKEN`:

```yaml
# This breaks fork PRs
- uses: SonarSource/sonarcloud-github-action@v2
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}  # Not available in forks!
```

Every community contribution fails CI. Contributors wait for maintainers, friction builds, contributions slow.

## The Fix: GITHUB_TOKEN Only

Our security workflow uses only the automatically-provided `GITHUB_TOKEN`:

```yaml
jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  # Available to forks!
```

## The Gitleaks Gotcha

Our first attempt had a dangerous config:

```toml
# .gitleaks.toml - DANGEROUS
[allowlist]
paths = [
  '''\.md$''',
]
```

This excludes all markdown from scanning. For a docs repo, that's most of the codebase—and exactly where secrets leak (tutorial code blocks with real API keys).

Fixed version:

```toml
# .gitleaks.toml - SAFE
[[rules]]
id = "example-api-key"
regex = '''sk-example-[a-zA-Z0-9]+'''
allowlist = { regexes = ['''sk-example-'''] }
```

Only explicit placeholder patterns are ignored.

## The 3-Layer Pipeline

| Layer | Tools | Secrets Required |
|-------|-------|------------------|
| Pre-Commit | Gitleaks, yamllint | None |
| PR Checks | Gitleaks Action, Dependency Review | GITHUB_TOKEN only |
| Post-Merge | Dependabot, Secret Scanning | Built into GitHub |

Total config: `.pre-commit-config.yaml`, `.gitleaks.toml`, `.github/workflows/security.yml`.

## The Norway Problem

Our yamllint workflow failed immediately:

```
[truthy] truthy value should be one of [false, true]
  3:1      error    on:
```

YAML 1.1 treats `on`, `off`, `yes`, `no` as booleans. Country code `NO` becomes `false`. GitHub Actions uses `on:` as a keyword.

Fix in `.yamllint.yml`:

```yaml
rules:
  truthy:
    allowed-values: ['true', 'false', 'on']
```

---

Full ADR: https://amiable-dev.github.io/amiable-templates/blog/2026/01/03/devsecops-for-a-docs-site-adr-005/
