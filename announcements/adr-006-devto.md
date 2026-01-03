# ADR-006 Dev.to Announcement

**Title:** SHA-Based Caching for Multi-Repo Documentation Aggregation

**Tags:** documentation, github, python, devops, caching

---

We built a system that pulls documentation from multiple GitHub repositories at build time. The key insight: you don't need to fetch content to check if it changed.

## The Problem

Templates across 3+ repos. Each with its own docs. Users don't want to visit three different GitHub repos.

## The Solution: Build-Time Aggregation with SHA Caching

### Step 1: Lightweight SHA Check

```python
async def get_commit_sha(self, owner: str, repo: str) -> str | None:
    """1 API request, returns just the SHA, not content."""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/HEAD"
    async with self._session.get(url) as resp:
        return (await resp.json())["sha"]
```

### Step 2: Cache Comparison

```python
def is_cached(self, template_id: str, commit_sha: str) -> bool:
    if template_id not in self.entries:
        return False
    return self.entries[template_id]["commit_sha"] == commit_sha
```

### Step 3: Fetch Only If Changed

If SHA matches → use cached content
If SHA differs → fetch fresh, update cache

**Result:**
```
Using cached content (SHA: 5a45454)
Using cached content (SHA: f23f22e)
Aggregation complete: 3/3 templates processed
```

## Rate Limit Strategy

| Endpoint | Limit | Our Usage |
|----------|-------|-----------|
| GitHub API | 5,000/hr with token | 1 req/repo for commit SHA |
| raw.githubusercontent.com | Bypasses API quota | All content fetches |

50 repos = 50 API requests per build. The 5,000/hr limit is plenty.

**Note:** We check the repo's HEAD commit SHA, not individual file SHAs. This means a code-only change still triggers a doc re-fetch—a deliberate tradeoff to keep API calls to 1 per repo.

## Content Transformation

Upstream docs have relative links that break. Transform:

```python
# Before: ![diagram](../assets/arch.png)
# After:  ![diagram](https://raw.githubusercontent.com/owner/repo/sha/assets/arch.png)
```

Plus source attribution:
```markdown
!!! info "Source Repository"
    From [owner/repo](https://github.com/owner/repo)
    Last synced: 2026-01-03 | Commit: `5a45454`
```

## Error Philosophy

**Never fail the build due to upstream issues.**

- Network error → use cached content
- Repo not found → skip, continue
- Rate limit → use cached content

But log every failure. Silent failures are worse than crashes.

---

Full ADR: https://amiable-dev.github.io/amiable-templates/blog/2026/01/03/build-time-documentation-aggregation-adr-006/
