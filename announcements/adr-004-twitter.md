# ADR-004 Twitter Announcement

Moved our docs CI/CD to GitHub Actions.

The goal: Reduce moving parts (1 vendor vs 3).
The trade-off: We killed PR previews.

For docs where changes are markdown diffs, we can live without them.

Bonus: yamllint tried to parse `on:` as a YAML 1.1 boolean.

https://amiable-dev.github.io/amiable-templates/blog/2026/01/03/cicd-for-a-docs-site-adr-004/

#DevOps #GitHubActions
