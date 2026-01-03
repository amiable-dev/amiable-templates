<p align="center">
  <a href="https://amiable-dev.github.io/amiable-templates">
    <img src="https://raw.githubusercontent.com/amiable-dev/amiable-templates/main/docs/img/logo.png" alt="Amiable Templates Logo" width="200">
  </a>
</p>

<h1 align="center">amiable-templates</h1>

<p align="center">
  <a href="https://github.com/amiable-dev/amiable-templates/actions/workflows/deploy.yml"><img src="https://github.com/amiable-dev/amiable-templates/actions/workflows/deploy.yml/badge.svg" alt="Deploy"></a>
  <a href="https://github.com/amiable-dev/amiable-templates/actions/workflows/security.yml"><img src="https://github.com/amiable-dev/amiable-templates/actions/workflows/security.yml/badge.svg" alt="Security"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
</p>

<p align="center">
  <em>A unified documentation portal for Railway deployment templates.</em>
</p>

## What is This?

amiable-templates is an open source documentation site that aggregates Railway deployment templates from multiple repositories into a single, searchable portal. It provides:

- **Template Grid** - Browse available templates with descriptions, features, and deploy links
- **Quick Start Guide** - Get deploying in minutes
- **Cross-Project Documentation** - Aggregated docs from template source repositories
- **Architecture Decision Records** - Transparent decision-making process

## Quick Start

### View the Site

Visit [amiable.dev/templates](https://amiable.dev/templates) (or your deployed URL).

### Local Development

```bash
# Clone the repository
git clone https://github.com/amiable-dev/amiable-templates.git
cd amiable-templates

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Aggregate template docs (requires GITHUB_TOKEN)
export GITHUB_TOKEN=ghp_your_token_here
python scripts/aggregate_templates.py

# Serve locally
mkdocs serve
```

The site will be available at `http://127.0.0.1:8000`.

## Available Templates

| Template | Description | Category |
|----------|-------------|----------|
| **LiteLLM + Langfuse Starter** | Production-ready LLM gateway with observability | Observability |
| **LiteLLM + Langfuse Production** | Enterprise-grade LLM proxy with backups and monitoring | Observability |
| **LLM Council** | Multi-model consensus system for AI decision-making | AI Infrastructure |

See `templates.yaml` for the full template registry.

## Project Structure

```
amiable-templates/
├── docs/                    # MkDocs source
│   ├── index.md            # Home page
│   ├── quickstart.md       # Quick Start guide
│   ├── templates/          # Template documentation (aggregated)
│   ├── adrs/               # Architecture Decision Records
│   └── stylesheets/        # Custom CSS
├── scripts/
│   └── aggregate_templates.py  # Doc aggregation script
├── templates.yaml          # Template registry
├── templates.schema.yaml   # Configuration schema
├── mkdocs.yml              # MkDocs configuration
└── .github/workflows/      # CI/CD pipelines
```

## Configuration

Templates are defined in `templates.yaml`:

```yaml
templates:
  - id: litellm-langfuse-starter
    repo:
      owner: "amiable-dev"
      name: "litellm-langfuse-railway"
    title: "LiteLLM + Langfuse Starter"
    description: "Production-ready LLM gateway with observability"
    category: observability
    directories:
      docs:
        - path: "starter/README.md"
          target: "overview.md"
```

See the [Template Configuration ADR](docs/adrs/ADR-003-template-configuration-system.md) for details.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Adding a Template

1. Fork this repository
2. Add your template to `templates.yaml`
3. Submit a pull request

Template requirements:
- Publicly accessible GitHub repository
- Clear documentation in the repository
- Working Railway deployment

### Development Setup

```bash
# Install pre-commit hooks (recommended)
pip install pre-commit
pre-commit install
```

## Architecture Decisions

This project uses Architecture Decision Records (ADRs) to document significant decisions:

| ADR | Title |
|-----|-------|
| [ADR-001](docs/adrs/ADR-001-project-structure-oss-standards.md) | Project Structure & OSS Standards |
| [ADR-002](docs/adrs/ADR-002-mkdocs-site-architecture.md) | MkDocs Site Architecture |
| [ADR-003](docs/adrs/ADR-003-template-configuration-system.md) | Template Configuration System |
| [ADR-004](docs/adrs/ADR-004-ci-cd-deployment.md) | CI/CD & Deployment |
| [ADR-005](docs/adrs/ADR-005-devsecops-implementation.md) | DevSecOps Implementation |
| [ADR-006](docs/adrs/ADR-006-cross-project-adr-aggregation.md) | Cross-Project Documentation Aggregation |

ADRs are reviewed by the [LLM Council](https://github.com/amiable-dev/llm-council) for multi-model architectural feedback.

## Security

- Secret scanning via Gitleaks (pre-commit + CI)
- Dependency updates via Dependabot
- Fork-friendly CI (no secrets required for PR checks)

See [SECURITY.md](SECURITY.md) for vulnerability reporting.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Related Projects

- [litellm-langfuse-railway](https://github.com/amiable-dev/litellm-langfuse-railway) - LLM gateway templates
- [llm-council](https://github.com/amiable-dev/llm-council) - Multi-model consensus system
