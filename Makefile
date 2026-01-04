# Makefile for amiable-templates
# See ADR-007 for design documentation.

.PHONY: validate validate-deep templates templates-json test test-cov serve build help

# Validation targets
validate: ## Validate templates.yaml (Level 1 + 2)
	@python scripts/template_manager.py validate

validate-deep: ## Validate with network checks (Level 3 - Phase 4)
	@python scripts/template_manager.py validate --deep

# Template listing
templates: ## List all templates
	@python scripts/template_manager.py list

templates-json: ## List templates as JSON
	@python scripts/template_manager.py list --format json

# Testing
test: ## Run unit tests
	@python -m pytest tests/ -v

test-cov: ## Run tests with coverage
	@python -m pytest tests/ --cov=scripts --cov-report=term-missing

# Development
serve: ## Start MkDocs development server
	mkdocs serve

build: validate ## Full build with validation
	python scripts/aggregate_templates.py
	mkdocs build --strict

# Documentation
docs: ## Generate documentation
	mkdocs build

# Default target
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
