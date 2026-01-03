# ADR-006 Hacker News Announcement

**Title:** SHA-Based Caching for Multi-Repo Documentation Aggregation

**URL:** https://amiable-dev.github.io/amiable-templates/blog/2026/01/03/build-time-documentation-aggregation-adr-006/

**Comment to post with submission:**

We built a system that pulls documentation from multiple GitHub repositories at build time. The interesting part is the caching strategy.

The naive approach: fetch everything on every build. Slow and hits rate limits.

Our approach: SHA-based cache invalidation. One lightweight API call (`GET /repos/owner/repo/commits/HEAD`) returns the current commit SHA. Compare against the cached SHA. If unchanged, skip the fetch entirely.

Content is fetched via raw.githubusercontent.com (bypasses API quota), not the API. So even cold builds only use N API requests where N = number of repos.

The tricky parts:
1. Link rewriting: relative links break when content moves. Transform to absolute GitHub URLs.
2. Image rewriting: point to raw.githubusercontent.com for direct embedding.
3. Error resilience: never fail the build due to upstream issues. Serve cached content, log warnings.

The tradeoff we accepted: changes aren't instant. Daily rebuilds + manual dispatch for urgent updates.

**Why not git submodules?** We wanted to avoid cloning repo history just to parse 3 markdown files.

**Why repo-level SHA, not file-level?** Keeps API calls to 1 per repo. Yes, a code-only commit triggers a doc re-fetch—over-fetching is better than under-fetching for documentation.

Source: https://github.com/amiable-dev/amiable-templates
