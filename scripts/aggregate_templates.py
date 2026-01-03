#!/usr/bin/env python3
"""
Build-time aggregation of template documentation from configured GitHub repositories.

Reads configuration from templates.yaml and fetches documentation at CI time.
Implements caching via commit SHA comparison to avoid redundant fetches.

See ADR-006 for design details.
"""

import asyncio
import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Constants
GITHUB_API_BASE = "https://api.github.com"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com"
CONFIG_FILE = "templates.yaml"
DEFAULT_CACHE_DIR = Path(".cache/templates")
DEFAULT_OUTPUT_DIR = Path("docs/templates")


@dataclass
class CacheManifest:
    """Tracks cached state for templates."""

    entries: dict[str, dict[str, Any]] = field(default_factory=dict)

    def is_cached(self, template_id: str, commit_sha: str) -> bool:
        """Check if template is cached with matching commit SHA."""
        if template_id not in self.entries:
            return False
        return self.entries[template_id].get("commit_sha") == commit_sha

    def update(self, template_id: str, commit_sha: str, files: list[str]) -> None:
        """Update cache entry for a template."""
        self.entries[template_id] = {
            "commit_sha": commit_sha,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "files": files,
        }

    @classmethod
    def load(cls, path: Path) -> "CacheManifest":
        """Load manifest from disk."""
        if path.exists():
            try:
                data = json.loads(path.read_text())
                return cls(entries=data)
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Failed to load cache manifest: {e}")
        return cls()

    def save(self, path: Path) -> None:
        """Save manifest to disk."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.entries, indent=2))


class GitHubFetcher:
    """Handles GitHub API interactions."""

    def __init__(self, token: str | None, concurrency: int = 5):
        self.token = token
        self.semaphore = asyncio.Semaphore(concurrency)
        self._session: aiohttp.ClientSession | None = None

    @property
    def headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "amiable-templates-aggregator/1.0",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def __aenter__(self) -> "GitHubFetcher":
        self._session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._session:
            await self._session.close()

    async def get_commit_sha(self, owner: str, repo: str) -> str | None:
        """Get the SHA of the default branch HEAD."""
        async with self.semaphore:
            url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits/HEAD"
            try:
                async with self._session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["sha"]
                    logger.error(
                        f"Failed to get HEAD SHA for {owner}/{repo}: {resp.status}"
                    )
                    return None
            except aiohttp.ClientError as e:
                logger.error(f"Network error getting SHA for {owner}/{repo}: {e}")
                return None

    async def fetch_file(
        self, owner: str, repo: str, sha: str, path: str
    ) -> str | None:
        """Fetch raw file content (no API rate limit)."""
        async with self.semaphore:
            url = f"{GITHUB_RAW_BASE}/{owner}/{repo}/{sha}/{path}"
            try:
                async with self._session.get(url) as resp:
                    if resp.status == 200:
                        return await resp.text()
                    logger.warning(f"File not found: {path} in {owner}/{repo}")
                    return None
            except aiohttp.ClientError as e:
                logger.error(f"Network error fetching {path}: {e}")
                return None


class ContentTransformer:
    """Transforms aggregated content for the unified site."""

    def __init__(self, owner: str, repo: str, commit_sha: str, source_path: str):
        self.owner = owner
        self.repo = repo
        self.commit_sha = commit_sha
        self.base_path = Path(source_path).parent

    def transform(self, content: str) -> str:
        """Apply all transformations to content."""
        content = self._rewrite_images(content)
        content = self._rewrite_links(content)
        content = self._add_attribution(content)
        return content

    def _rewrite_images(self, content: str) -> str:
        """Rewrite relative image paths to raw.githubusercontent.com URLs."""
        pattern = r"!\[([^\]]*)\]\(([^)]+)\)"

        def replace_image(match: re.Match) -> str:
            alt_text = match.group(1)
            path = match.group(2)

            # Skip already-absolute URLs
            if path.startswith(("http://", "https://", "//")):
                return match.group(0)

            # Resolve relative path
            resolved = self._resolve_path(path)
            absolute_url = f"{GITHUB_RAW_BASE}/{self.owner}/{self.repo}/{self.commit_sha}/{resolved}"
            return f"![{alt_text}]({absolute_url})"

        return re.sub(pattern, replace_image, content)

    def _rewrite_links(self, content: str) -> str:
        """Rewrite relative markdown links to GitHub blob URLs."""
        pattern = r"\[([^\]]+)\]\(([^)]+)\)"

        def replace_link(match: re.Match) -> str:
            text = match.group(1)
            path = match.group(2)

            # Skip already-absolute URLs and anchors
            if path.startswith(("http://", "https://", "//", "#", "mailto:")):
                return match.group(0)

            # Check if it's a markdown file
            if path.endswith(".md"):
                resolved = self._resolve_path(path)
                absolute_url = f"https://github.com/{self.owner}/{self.repo}/blob/{self.commit_sha}/{resolved}"
                return f"[{text}]({absolute_url})"

            return match.group(0)

        return re.sub(pattern, replace_link, content)

    def _resolve_path(self, relative_path: str) -> str:
        """Resolve a relative path against the base directory."""
        # Remove leading ./
        if relative_path.startswith("./"):
            relative_path = relative_path[2:]

        # Resolve against base path
        resolved = (self.base_path / relative_path).as_posix()

        # Normalize (remove ../ etc)
        parts = []
        for part in resolved.split("/"):
            if part == "..":
                if parts:
                    parts.pop()
            elif part and part != ".":
                parts.append(part)

        return "/".join(parts)

    def _add_attribution(self, content: str) -> str:
        """Add source attribution to content."""
        source_url = f"https://github.com/{self.owner}/{self.repo}"
        now = datetime.utcnow().strftime("%Y-%m-%d")

        attribution = f"""!!! info "Source Repository"
    This documentation is from [{self.owner}/{self.repo}]({source_url}).
    Last synced: {now} | Commit: `{self.commit_sha[:7]}`

"""
        return attribution + content


async def aggregate_template(
    template: dict[str, Any],
    fetcher: GitHubFetcher,
    cache: CacheManifest,
    output_dir: Path,
) -> tuple[str, str]:
    """Aggregate a single template's documentation."""
    template_id = template["id"]
    owner = template["repo"]["owner"]
    repo_name = template["repo"]["name"]
    repo_full = f"{owner}/{repo_name}"

    logger.info(f"Processing template: {template_id} ({repo_full})")

    # Get current commit SHA
    commit_sha = await fetcher.get_commit_sha(owner, repo_name)
    if not commit_sha:
        logger.warning(f"Could not get commit SHA for {repo_full}, skipping")
        return template_id, ""

    # Check cache
    if cache.is_cached(template_id, commit_sha):
        logger.info(f"  Using cached content (SHA: {commit_sha[:7]})")
        return template_id, commit_sha

    logger.info(f"  Fetching fresh content (SHA: {commit_sha[:7]})")

    # Prepare output directory
    template_output = output_dir / template_id
    template_output.mkdir(parents=True, exist_ok=True)

    # Fetch and process each doc
    fetched_files = []
    docs = template.get("directories", {}).get("docs", [])

    for doc in docs:
        source_path = doc["path"]
        target_name = doc["target"]

        # Fetch content
        content = await fetcher.fetch_file(owner, repo_name, commit_sha, source_path)
        if not content:
            logger.warning(f"  Could not fetch {source_path}")
            continue

        # Transform content
        transformer = ContentTransformer(owner, repo_name, commit_sha, source_path)
        content = transformer.transform(content)

        # Write output
        output_file = template_output / target_name
        output_file.write_text(content)
        fetched_files.append(target_name)
        logger.info(f"  Wrote {target_name}")

    # Update cache
    cache.update(template_id, commit_sha, fetched_files)

    return template_id, commit_sha


def load_config(config_path: str = CONFIG_FILE) -> dict[str, Any]:
    """Load configuration from templates.yaml."""
    path = Path(config_path)
    if not path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(path) as f:
        return yaml.safe_load(f)


async def main() -> None:
    """Main aggregation entry point."""
    # Load configuration
    try:
        config = load_config()
    except FileNotFoundError:
        return

    # Get settings
    settings = config.get("settings", {})
    cache_dir = Path(settings.get("cache", {}).get("directory", DEFAULT_CACHE_DIR))
    output_dir = Path(settings.get("output", {}).get("docs_directory", DEFAULT_OUTPUT_DIR))
    concurrency = settings.get("github_api", {}).get("concurrency", 5)

    # Get GitHub token
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        logger.warning("GITHUB_TOKEN not set - API rate limits will apply")

    # Load cache manifest
    manifest_path = cache_dir / "manifest.json"
    cache = CacheManifest.load(manifest_path)

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Aggregate all templates
    templates = config.get("templates", [])
    logger.info(f"Aggregating {len(templates)} templates...")

    async with GitHubFetcher(token, concurrency) as fetcher:
        results = await asyncio.gather(
            *[
                aggregate_template(template, fetcher, cache, output_dir)
                for template in templates
            ],
            return_exceptions=True,
        )

        success_count = 0
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Aggregation error: {result}")
            elif result[1]:  # Has commit SHA = success
                success_count += 1

    # Save cache manifest
    cache.save(manifest_path)

    logger.info(f"Aggregation complete: {success_count}/{len(templates)} templates processed")


if __name__ == "__main__":
    asyncio.run(main())
