#!/usr/bin/env python3
"""
Cross-post Hugo articles to Dev.to.

Usage:
    # Publish a single article
    python devto.py --file site/content/android/01-Recipes/Analysis/js_obfuscator.md

    # Publish all new articles (not yet on Dev.to)
    python devto.py --sync

    # Dry run (preview without publishing)
    python devto.py --sync --dry-run

    # List published articles on Dev.to
    python devto.py --list

Environment:
    DEVTO_API_KEY - Dev.to API key (required)
    HUGO_BASE_URL - Base URL of Hugo site (default: https://overkazaf.github.io/reverse_engineering)
"""

import argparse
import json
import os
import re
import ssl
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# Handle macOS Python SSL certificate issues
try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()
    SSL_CONTEXT.check_hostname = False
    SSL_CONTEXT.verify_mode = ssl.CERT_NONE

API_BASE = "https://dev.to/api"
HUGO_BASE_URL = os.environ.get(
    "HUGO_BASE_URL", "https://overkazaf.github.io/reverse_engineering"
)
SITE_CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "site" / "content"


def get_api_key():
    key = os.environ.get("DEVTO_API_KEY", "")
    if not key:
        print("Error: DEVTO_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    return key


def api_request(method, endpoint, data=None):
    """Make an API request to Dev.to."""
    url = f"{API_BASE}{endpoint}"
    headers = {
        "api-key": get_api_key(),
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "HugoCrossPoster/1.0",
    }
    body = json.dumps(data).encode() if data else None
    req = Request(url, data=body, headers=headers, method=method)

    try:
        with urlopen(req, context=SSL_CONTEXT) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        error_body = e.read().decode()
        print(f"API Error {e.code}: {error_body}", file=sys.stderr)
        raise


def parse_hugo_frontmatter(filepath):
    """Parse Hugo markdown frontmatter and body."""
    content = Path(filepath).read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    frontmatter = {}
    for line in parts[1].strip().split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if value.startswith("[") and value.endswith("]"):
                value = [t.strip().strip('"').strip("'") for t in value[1:-1].split(",")]
            frontmatter[key] = value

    body = parts[2].strip()
    return frontmatter, body


def hugo_path_to_canonical_url(filepath):
    """Convert Hugo file path to canonical URL."""
    rel = Path(filepath).resolve().relative_to(SITE_CONTENT_DIR)
    slug = str(rel).replace(".md", "/").lower()
    return f"{HUGO_BASE_URL}/{slug}"


def prepare_devto_body(body, filepath):
    """Convert Hugo markdown to Dev.to compatible markdown."""
    # Remove Hugo shortcodes
    body = re.sub(r'\{\{<.*?>}}', '', body)
    body = re.sub(r'\{\{%.*?%}}', '', body)

    # Convert Hugo blockquote alerts to bold callouts (Dev.to doesn't support GFM alerts)
    def replace_alert(match):
        alert_type = match.group(1).upper()
        title = match.group(2) or ""
        content = match.group(3)
        # Remove > prefix from content lines
        content_lines = []
        for line in content.split("\n"):
            if line.startswith("> "):
                content_lines.append(line[2:])
            elif line.strip() == ">":
                content_lines.append("")
            else:
                content_lines.append(line)
        inner = "\n".join(content_lines).strip()
        header = f"**{alert_type}**" + (f" {title}" if title else "")
        return f"> {header}\n>\n" + "\n".join(f"> {l}" if l else ">" for l in inner.split("\n"))

    body = re.sub(
        r'^> \[!(\w+)\]\s*(.*?)\n((?:>.*\n)*)',
        replace_alert,
        body,
        flags=re.MULTILINE,
    )

    # Add canonical URL footer
    canonical = hugo_path_to_canonical_url(filepath)
    body += f"\n\n---\n\n*Originally published at [{HUGO_BASE_URL}]({canonical})*\n"

    return body


def prepare_article(filepath):
    """Prepare article data for Dev.to API."""
    frontmatter, body = parse_hugo_frontmatter(filepath)

    title = frontmatter.get("title", Path(filepath).stem)
    tags_raw = frontmatter.get("tags", [])
    if isinstance(tags_raw, str):
        tags_raw = [tags_raw]

    # Dev.to: max 4 tags, alphanumeric + hyphen, max 30 chars
    tags = []
    for t in tags_raw:
        tag = re.sub(r'[^a-zA-Z0-9]', '', t.lower())[:30]
        if tag and tag not in tags:
            tags.append(tag)
        if len(tags) >= 4:
            break

    # Ensure at least one tag
    if not tags:
        tags = ["android", "reverseengineering"]

    canonical_url = hugo_path_to_canonical_url(filepath)
    devto_body = prepare_devto_body(body, filepath)

    return {
        "article": {
            "title": title,
            "body_markdown": devto_body,
            "published": False,  # Create as draft first
            "tags": tags,
            "canonical_url": canonical_url,
            "series": "Android Reverse Engineering Cookbook",
        }
    }


def get_published_articles():
    """Get all articles from Dev.to account."""
    articles = []
    page = 1
    while True:
        result = api_request("GET", f"/articles/me/all?page={page}&per_page=100")
        if not result:
            break
        articles.extend(result)
        if len(result) < 100:
            break
        page += 1
    return articles


def get_published_canonicals():
    """Get set of canonical URLs already published."""
    articles = get_published_articles()
    return {a.get("canonical_url", "") for a in articles}


def publish_article(filepath, dry_run=False):
    """Publish a single article to Dev.to."""
    data = prepare_article(filepath)
    title = data["article"]["title"]

    if dry_run:
        print(f"  [DRY RUN] Would publish: {title}")
        print(f"    Tags: {data['article']['tags']}")
        print(f"    Canonical: {data['article']['canonical_url']}")
        return None

    print(f"  Publishing: {title} ...", end=" ", flush=True)
    result = api_request("POST", "/articles", data)
    print(f"OK (id={result['id']}, url={result['url']})")
    return result


def find_all_articles():
    """Find all publishable Hugo articles."""
    articles = []
    for md_file in sorted(SITE_CONTENT_DIR.rglob("*.md")):
        if md_file.name == "_index.md":
            continue
        # Only android content for now
        if "android" not in str(md_file):
            continue
        frontmatter, body = parse_hugo_frontmatter(md_file)
        if not frontmatter.get("title"):
            continue
        # Skip very short articles
        if len(body) < 500:
            continue
        articles.append(md_file)
    return articles


def cmd_publish(args):
    """Publish a single file."""
    result = publish_article(args.file, dry_run=args.dry_run)
    if result:
        print(f"\nDraft created: {result['url']}")
        print("Go to Dev.to dashboard to review and publish.")


def cmd_sync(args):
    """Sync all new articles."""
    print("Fetching published articles from Dev.to...")
    published = get_published_canonicals()
    print(f"  Found {len(published)} published articles\n")

    all_articles = find_all_articles()
    print(f"Found {len(all_articles)} local articles\n")

    new_count = 0
    for filepath in all_articles:
        canonical = hugo_path_to_canonical_url(filepath)
        if canonical in published:
            continue
        new_count += 1
        publish_article(filepath, dry_run=args.dry_run)
        if not args.dry_run:
            time.sleep(1)  # Rate limiting

    if new_count == 0:
        print("All articles already synced!")
    else:
        action = "would publish" if args.dry_run else "published"
        print(f"\n{action} {new_count} new articles as drafts")


def cmd_list(args):
    """List published articles."""
    articles = get_published_articles()
    print(f"Total articles on Dev.to: {len(articles)}\n")
    for a in articles:
        status = "published" if a.get("published") else "draft"
        print(f"  [{status}] {a['title']}")
        print(f"    URL: {a.get('url', 'N/A')}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Cross-post Hugo articles to Dev.to")
    sub = parser.add_subparsers(dest="command")

    p_publish = sub.add_parser("publish", help="Publish a single article")
    p_publish.add_argument("--file", required=True, help="Path to Hugo markdown file")
    p_publish.add_argument("--dry-run", action="store_true")
    p_publish.set_defaults(func=cmd_publish)

    p_sync = sub.add_parser("sync", help="Sync all new articles to Dev.to")
    p_sync.add_argument("--dry-run", action="store_true")
    p_sync.set_defaults(func=cmd_sync)

    p_list = sub.add_parser("list", help="List articles on Dev.to")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
