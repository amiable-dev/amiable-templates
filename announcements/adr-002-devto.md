# ADR-002 Dev.to Announcement

**Title:** Building a Template Grid in MkDocs Material Without React

**Tags:** mkdocs, css, documentation, webdev, python

---

We needed a documentation site to showcase Railway deployment templates. The grid needed to be scannable, attractive, and work in dark mode—without adding React or Node to our Python-based project.

## The Options

| Option | Pros | Cons |
|--------|------|------|
| MkDocs Material | Matches Python scripts, built-in search | Less flexible than custom |
| Docusaurus | Powerful, React components | Adds Node to Python stack |
| Custom | Full control | Weeks of work |

We went with MkDocs Material for one reason: **consistency**. Our other projects use it.

## The Template Grid

Pure CSS Grid with markdown content. The key is the `markdown="1"` attribute, which tells MkDocs Material to process markdown inside HTML elements:

```html
<div class="template-grid" markdown="1">
<div class="template-card" markdown="1">

### Template Name

Description and features here.

**Estimated Cost:** ~$29-68/month

[:octicons-rocket-16: Deploy](https://railway.app/template/...)

</div>
</div>
```

Note: You need the `md_in_html` extension enabled in your `mkdocs.yml`.

## The CSS

```css
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
}

.template-card {
  border: 1px solid var(--md-default-fg-color--lightest);
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.template-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}
```

## Dark Mode

MkDocs Material auto-detects system preference with manual override:

```yaml
theme:
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      toggle:
        icon: material/brightness-7
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      toggle:
        icon: material/brightness-4
```

No custom JavaScript needed for the toggle.

## The Trade-off

MkDocs Material does use JavaScript under the hood (RxJS for search, etc.). What we avoided was adding custom JavaScript or a separate build pipeline. The markdown-in-HTML pattern keeps everything in markdown files that any contributor can edit.

Full ADR with more details: https://amiable-dev.github.io/amiable-templates/blog/2026/01/03/choosing-mkdocs-material-adr-002-site-architecture/

Source code: https://github.com/amiable-dev/amiable-templates
