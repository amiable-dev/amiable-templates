# Contributing to Amiable Templates

Thank you for your interest in contributing to Amiable Templates! This document provides guidelines and instructions for contributing to our documentation site.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Ways to Contribute

### 1. Request a New Template

If you'd like to see a new Railway template documented:

1. Check existing [issues](https://github.com/amiable-dev/amiable-templates/issues) to avoid duplicates
2. Open a [Feature Request](https://github.com/amiable-dev/amiable-templates/issues/new?template=feature_request.md)
3. Provide the template repository URL and description

### 2. Improve Documentation

- Fix typos or unclear explanations
- Add examples or clarifications
- Improve navigation or structure

### 3. Report Issues

- Broken links
- Build failures
- Display problems

## Getting Started

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Git

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/amiable-templates.git
   cd amiable-templates
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Create environment file (for aggregation script):**
   ```bash
   cp .env.example .env
   # Add your GITHUB_TOKEN for API access
   ```

4. **Run the docs locally:**
   ```bash
   uv run mkdocs serve
   ```

5. **Visit** http://localhost:8000 to preview the site

### Project Structure

```
amiable-templates/
├── docs/                    # Documentation source
│   ├── index.md            # Home page
│   ├── quickstart.md       # Quick start guide
│   ├── templates/          # Template documentation
│   │   └── index.md        # Template grid
│   ├── adrs/               # Architecture Decision Records
│   └── blog/               # Blog posts
├── scripts/                # Build scripts
│   └── aggregate_templates.py
├── templates.yaml          # Template registry
├── mkdocs.yml             # MkDocs configuration
└── requirements.txt       # Python dependencies
```

## Development Workflow

### Creating a Branch

Create a feature branch from `main`:

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features or templates
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `chore/` - Maintenance tasks

### Making Changes

1. **Edit documentation** in the `docs/` directory
2. **Preview locally:**
   ```bash
   uv run mkdocs serve
   ```
3. **Check for broken links** (run lychee or similar)
4. **Commit your changes**

### Commit Messages

We follow conventional commit format:

```
<type>(<scope>): <description>

[optional body]
```

**Types:**
- `feat`: New feature or template
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no content change
- `chore`: Maintenance tasks

**Examples:**
```
docs(templates): Add LiteLLM configuration examples

feat(grid): Add filtering by category

fix(links): Correct broken GitHub links in ADR-001
```

### Pull Requests

1. **Push your branch:**
   ```bash
   git push -u origin feature/your-feature-name
   ```

2. **Create a pull request** via GitHub

3. **Fill out the PR template** with:
   - Summary of changes
   - Screenshots (if UI changes)
   - Checklist completion

4. **Address review feedback** promptly

5. **Ensure CI passes** before requesting merge

## Adding a New Template

To add a new template to the documentation site:

1. **Ensure the template repo exists** and has documentation

2. **Update `templates.yaml`:**
   ```yaml
   templates:
     - id: your-template-name
       repo:
         owner: "amiable-dev"
         name: "your-template-repo"
       title: "Your Template Title"
       description: "Brief description"
       category: observability  # or ai-infrastructure, etc.
       directories:
         template: "."
         docs:
           - path: "README.md"
             target: "overview.md"
       links:
         github: "https://github.com/amiable-dev/your-template-repo"
   ```

3. **Validate the schema:**
   ```bash
   check-jsonschema --schemafile templates.schema.yaml templates.yaml
   ```

4. **Run aggregation locally:**
   ```bash
   python scripts/aggregate_templates.py
   ```

5. **Preview the site** to verify the template appears correctly

6. **Submit a PR** with your changes

### templates.yaml Schema

The `templates.yaml` file is validated against `templates.schema.yaml`. Key fields:

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier (lowercase, hyphens) |
| `repo.owner` | Yes | GitHub organization or user |
| `repo.name` | Yes | Repository name |
| `title` | Yes | Display title |
| `description` | Yes | Brief description for template grid |
| `category` | Yes | Category ID (e.g., `observability`) |
| `directories.docs` | Yes | List of docs to fetch |
| `tags` | No | Tags for filtering |
| `features` | No | Feature highlights |
| `estimated_cost` | No | Cost estimate object |
| `links.railway_template` | No | Railway deploy URL |
| `links.github` | No | GitHub repository URL |

For the full schema, see `templates.schema.yaml` or [ADR-003](docs/adrs/ADR-003-template-configuration-system.md).

## Writing Documentation

### Style Guide

- Use clear, concise language
- Include code examples where helpful
- Use admonitions for warnings, tips, notes
- Keep paragraphs short (3-4 sentences max)

### MkDocs Features

**Admonitions:**
```markdown
!!! note "Title"
    Note content here.

!!! warning
    Warning content here.

!!! tip "Pro Tip"
    Helpful tip here.
```

**Code blocks with titles:**
```markdown
```yaml title="mkdocs.yml"
site_name: My Site
```
```

**Tabs:**
```markdown
=== "Python"
    ```python
    print("Hello")
    ```

=== "JavaScript"
    ```javascript
    console.log("Hello");
    ```
```

## Issue Labels

| Label | Description |
|-------|-------------|
| `bug` | Site issues, broken links |
| `enhancement` | Site improvements |
| `documentation` | Documentation updates |
| `good-first-issue` | Good for newcomers |
| `help-wanted` | Extra attention needed |
| `template-request` | Request for new template |

## Questions?

- Check existing [Discussions](https://github.com/amiable-dev/amiable-templates/discussions)
- Open a new Discussion for questions
- See [SUPPORT.md](SUPPORT.md) for support channels

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
