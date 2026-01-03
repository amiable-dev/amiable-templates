# ADR-006 LinkedIn Announcement

We have templates across multiple repositories. Each has its own documentation. Users shouldn't have to visit three repos to understand their options.

**The solution: Build-time documentation aggregation.**

Here's what made it work:

**SHA-based caching**

Don't fetch content to check if it changed. One lightweight API call (`GET /repos/owner/repo/commits/HEAD`) returns the current SHA. Compare against cached SHA. If unchanged, skip the fetch entirely.

Result: Cached builds use 0 content fetches.

**Content transformation**

Raw upstream docs have relative links that break when moved. Our `ContentTransformer` rewrites:
- Links → absolute GitHub URLs
- Images → raw.githubusercontent.com URLs
- Adds source attribution with sync date

**Graceful degradation**

If upstream is down, serve cached content. The build continues, but CI logs show every failure for investigation. Repo not found? Skip it, log warning, continue.

But be loud about failures—CI logs show every fetch error.

**The rate limit trick**

GitHub API: 5,000 requests/hour with `GITHUB_TOKEN`
Raw content: Does not consume API quota (bypasses rate limits)

We use API for metadata (1 req/repo), raw URLs for content. Even 50 repos = 50 API requests per build.

Full write-up with code: https://amiable-dev.github.io/amiable-templates/blog/2026/01/03/build-time-documentation-aggregation-adr-006/

How do you handle multi-repo documentation?
