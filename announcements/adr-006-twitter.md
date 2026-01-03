# ADR-006 Twitter Announcement

Built a docs aggregation system that pulls from multiple GitHub repos at build time.

The trick: SHA-based caching.
- 1 API call per repo to check commit SHA
- Content fetched from raw.githubusercontent.com (bypasses API quota)
- Cache hits reuse local content

https://amiable-dev.github.io/amiable-templates/blog/2026/01/03/build-time-documentation-aggregation-adr-006/

How do you handle multi-repo docs aggregation?

#Documentation #GitHubAPI #DevOps
