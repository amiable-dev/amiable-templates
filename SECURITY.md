# Security Policy

## Scope

This security policy covers the **amiable-templates** documentation site and its build infrastructure. For security issues in individual template repositories, please report to those repositories directly.

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please report vulnerabilities via one of these methods:

1. **GitHub Security Advisories** (Preferred)
   - Go to the [Security tab](https://github.com/amiable-dev/amiable-templates/security)
   - Click "Report a vulnerability"
   - Fill out the private security advisory form

2. **Email**
   - Send details to: security@amiable.dev

### What to Include

Please include:

- Description of the vulnerability
- Steps to reproduce
- Affected components (build scripts, CI/CD, dependencies)
- Potential impact
- Any suggested fixes (optional)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Resolution Target**: Within 90 days (depending on severity)

## Security Considerations

### Supply Chain Security

This documentation site aggregates content from multiple repositories. Security measures include:

- **Curated Sources Only**: Only repositories listed in `templates.yaml` are fetched
- **No Code Execution**: Aggregated content is markdown only, no executable code
- **CI-Time Fetch**: Content is fetched at build time, not runtime
- **Dependency Scanning**: Automated via Dependabot and Snyk

### GitHub Actions Security

- All actions pinned to specific SHA versions
- Minimal permissions (least privilege)
- No secrets exposed to fork PRs
- Gitleaks scanning for secret detection

### What We DON'T Handle

Report to the appropriate upstream repository for:

- **LiteLLM vulnerabilities**: [litellm/litellm](https://github.com/BerriAI/litellm/security)
- **Langfuse vulnerabilities**: [langfuse/langfuse](https://github.com/langfuse/langfuse/security)
- **MkDocs vulnerabilities**: [mkdocs/mkdocs](https://github.com/mkdocs/mkdocs/security)
- **Template-specific issues**: See individual template repositories

## Security Best Practices for Contributors

### Before Committing

- Never commit API keys or secrets
- Use `.env` files (git-ignored) for local development
- Review diffs before pushing

### Pre-commit Hooks

Install pre-commit hooks to catch secrets before they're committed:

```bash
pip install pre-commit
pre-commit install
```

This enables:
- **Gitleaks**: Secret detection
- **YAML lint**: Configuration validation

## Acknowledgments

We thank the security researchers who have helped improve the security of our projects:

- (Your name could be here!)
