# ADR-002 Hacker News Announcement

**Title:** MkDocs Material grid layout using CSS Grid and markdown="1" attribute

**URL:** https://amiable-dev.github.io/amiable-templates/blog/2026/01/03/choosing-mkdocs-material-adr-002-site-architecture/

**Comment to post with submission:**

We chose MkDocs Material over Docusaurus to keep our stack Python-exclusive. Our aggregation scripts are Python, and adding React/Node for the docs site would have split the tooling.

The template grid is built with CSS Grid and the `markdown="1"` attribute (requires `md_in_html` extension). This lets you nest standard markdown inside HTML divs:

```html
<div class="template-card" markdown="1">
### Template Name
Features here...
</div>
```

Trade-off: MkDocs Material itself uses JavaScript (RxJS for search). What we avoided was custom JavaScript or a separate build pipeline—everything stays as markdown files.

Source: https://github.com/amiable-dev/amiable-templates
