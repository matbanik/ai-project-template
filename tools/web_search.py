#!/usr/bin/env python3
"""
Web Search Tool
===============
Search the web using multiple search engine APIs.

## AI Agent Usage Guide

Prefer --output to persist results (avoids console truncation):
    python web_search.py "query" -o searches/ -t task-name

Results saved as: searches/YYYY-MM-DD/HH-MM-SS-{engine}[-task-{task}]-{query-slug}.json

## Quick Reference

    # Basic search (console output)
    python web_search.py "your search query"

    # Save to JSON (recommended for AI workflows)
    python web_search.py "query" --output searches/
    python web_search.py "query" -o searches/ --task seo-research

## Engine Selection Priority (for AI Agents)

Default order - use these unless user specifies otherwise:
    1. tavily   - AI-optimized snippets, 1000 free/month (RECOMMENDED)
    2. google   - Complex queries, 100 free/day
    3. brave    - General search, 2000 free/month
    4. duckduckgo - Backup, free, no API key

Only use if explicitly instructed:
    5. serpapi  - Multi-engine, 100 free TOTAL (conserve)
    6. serper   - Fast Google SERP, 2500 free TOTAL (conserve)

Requirements:
    pip install requests httpx beautifulsoup4

APIs (configured in api-keys.json or api-keys.local.json):
    - Tavily: 1000 free queries/month (resets monthly)
    - Google Custom Search: 100 free queries/day
    - Brave Search: 2000 free queries/month
    - DuckDuckGo: Free, no API key required
    - SerpApi: 100 free queries total (one-time)
    - Serper: 2500 free queries total (one-time)
"""

import argparse
import json
import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta

# Optional async imports for DuckDuckGo
try:
    import httpx
    from bs4 import BeautifulSoup
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False


def load_api_keys() -> Dict:
    """Load API keys from api-keys.local.json or api-keys.json."""
    # Try local keys first (for development with actual credentials)
    local_keys_path = Path(__file__).parent.parent / "api-keys.local.json"
    if local_keys_path.exists():
        with open(local_keys_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # Fall back to standard api-keys.json
    api_keys_path = Path(__file__).parent.parent / "api-keys.json"
    if not api_keys_path.exists():
        print(f"[ERROR] API keys file not found: {api_keys_path}")
        sys.exit(1)

    with open(api_keys_path, "r", encoding="utf-8") as f:
        return json.load(f)


def search_google(query: str, count: int = 5) -> List[Dict]:
    """Search using Google Custom Search API."""
    keys = load_api_keys()

    if "google_search" not in keys:
        print("[ERROR] Google Search not configured in api-keys.json")
        return []

    api_key = keys["google_search"]["api_key"]
    cse_id = keys["google_search"]["cse_id"]

    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={urllib.parse.quote(query)}&num={min(count, 10)}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())

        if "error" in data:
            print(f"[ERROR] Google API: {data['error']['message']}")
            return []

        results = []
        for item in data.get("items", []):
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "url": item.get("link", ""),
                "source": "google"
            })

        return results

    except urllib.error.HTTPError as e:
        print(f"[ERROR] HTTP {e.code}: {e.reason}")
        return []
    except Exception as e:
        print(f"[ERROR] {e}")
        return []


def search_brave(query: str, count: int = 5) -> List[Dict]:
    """Search using Brave Search API."""
    keys = load_api_keys()

    if "brave_search" not in keys:
        print("[ERROR] Brave Search not configured in api-keys.json")
        return []

    api_key = keys["brave_search"]["api_key"]

    url = f"https://api.search.brave.com/res/v1/web/search?q={urllib.parse.quote(query)}&count={min(count, 20)}"

    try:
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/json")
        req.add_header("X-Subscription-Token", api_key)

        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())

        results = []
        for item in data.get("web", {}).get("results", []):
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("description", ""),
                "url": item.get("url", ""),
                "source": "brave"
            })

        return results

    except urllib.error.HTTPError as e:
        print(f"[ERROR] HTTP {e.code}: {e.reason}")
        return []
    except Exception as e:
        print(f"[ERROR] {e}")
        return []




def search_duckduckgo_sync(query: str, count: int = 10) -> List[Dict]:
    """
    Search DuckDuckGo using HTML scraping (synchronous wrapper).
    No API key required - uses public HTML endpoint.
    """
    if not DUCKDUCKGO_AVAILABLE:
        print("[ERROR] DuckDuckGo requires: pip install httpx beautifulsoup4")
        return []
    
    import asyncio
    
    async def _async_search():
        return await _search_duckduckgo_async(query, count)
    
    # Run async function in sync context
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(_async_search())


async def _search_duckduckgo_async(query: str, max_results: int = 10) -> List[Dict]:
    """
    Async DuckDuckGo search implementation.
    Scrapes the HTML endpoint - no API key needed but subject to rate limits.
    """
    BASE_URL = "https://html.duckduckgo.com/html"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        # Create form data for POST request
        data = {
            "q": query,
            "b": "",
            "kl": "",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                BASE_URL, data=data, headers=HEADERS, timeout=30.0
            )
            response.raise_for_status()
        
        # Parse HTML response
        soup = BeautifulSoup(response.text, "html.parser")
        if not soup:
            print("[ERROR] Failed to parse DuckDuckGo response")
            return []
        
        results = []
        for result in soup.select(".result"):
            title_elem = result.select_one(".result__title")
            if not title_elem:
                continue
            
            link_elem = title_elem.find("a")
            if not link_elem:
                continue
            
            title = link_elem.get_text(strip=True)
            link = link_elem.get("href", "")
            
            # Skip ad results
            if "y.js" in link:
                continue
            
            # Clean up DuckDuckGo redirect URLs
            if link.startswith("//duckduckgo.com/l/?uddg="):
                link = urllib.parse.unquote(link.split("uddg=")[1].split("&")[0])
            
            snippet_elem = result.select_one(".result__snippet")
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
            
            results.append({
                "title": title,
                "snippet": snippet,
                "url": link,
                "source": "duckduckgo",
                "position": len(results) + 1
            })
            
            if len(results) >= max_results:
                break
        
        return results
    
    except Exception as e:
        print(f"[ERROR] DuckDuckGo: {e}")
        return []


# =============================================================================
# ADDITIONAL SEARCH ENGINES: Serper, Tavily, SerpApi
# =============================================================================
# AI Agent: These provide additional search options with different strengths:
#   - serper: Fast Google SERP data, 2500 free queries (no CC)
#   - tavily: AI-optimized search with good snippets, 1000 free/month
#   - serpapi: Multi-engine support (Google, Bing, Yahoo), 100 free total
# =============================================================================

def search_serper(query: str, count: int = 5) -> List[Dict]:
    """
    Search using Serper.dev Google SERP API.
    Fast, reliable Google results. 2500 free queries (no CC required).
    """
    keys = load_api_keys()

    if "serper" not in keys:
        print("[ERROR] Serper not configured in api-keys.json")
        return []

    api_key = keys["serper"]["api_key"]

    try:
        data = json.dumps({"q": query, "num": min(count, 100)}).encode('utf-8')
        req = urllib.request.Request(
            "https://google.serper.dev/search",
            data=data,
            headers={
                "X-API-KEY": api_key,
                "Content-Type": "application/json"
            }
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())

        results = []
        for item in result.get("organic", [])[:count]:
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "url": item.get("link", ""),
                "source": "serper",
                "position": item.get("position", len(results) + 1)
            })

        return results

    except urllib.error.HTTPError as e:
        print(f"[ERROR] Serper HTTP {e.code}: {e.reason}")
        return []
    except Exception as e:
        print(f"[ERROR] Serper: {e}")
        return []


def search_tavily(query: str, count: int = 5) -> List[Dict]:
    """
    Search using Tavily AI-optimized search API.
    Designed for AI agents. 1000 free calls/month.
    """
    keys = load_api_keys()

    if "tavily" not in keys:
        print("[ERROR] Tavily not configured in api-keys.json")
        return []

    api_key = keys["tavily"]["api_key"]

    try:
        data = json.dumps({
            "api_key": api_key,
            "query": query,
            "max_results": min(count, 20),
            "search_depth": "basic"
        }).encode('utf-8')

        req = urllib.request.Request(
            "https://api.tavily.com/search",
            data=data,
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())

        results = []
        for i, item in enumerate(result.get("results", [])[:count], 1):
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("content", ""),
                "url": item.get("url", ""),
                "source": "tavily",
                "position": i,
                "score": item.get("score", None)
            })

        return results

    except urllib.error.HTTPError as e:
        print(f"[ERROR] Tavily HTTP {e.code}: {e.reason}")
        return []
    except Exception as e:
        print(f"[ERROR] Tavily: {e}")
        return []


def search_serpapi(query: str, count: int = 5) -> List[Dict]:
    """
    Search using SerpApi (supports Google, Bing, Yahoo, etc).
    100 free searches total (one-time credit).
    """
    keys = load_api_keys()

    if "serpapi" not in keys:
        print("[ERROR] SerpApi not configured in api-keys.json")
        return []

    api_key = keys["serpapi"]["api_key"]
    params = urllib.parse.urlencode({
        "q": query,
        "api_key": api_key,
        "num": min(count, 100),
        "engine": "google"
    })

    try:
        url = f"https://serpapi.com/search.json?{params}"
        req = urllib.request.Request(url)

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())

        results = []
        for item in result.get("organic_results", [])[:count]:
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "url": item.get("link", ""),
                "source": "serpapi",
                "position": item.get("position", len(results) + 1)
            })

        return results

    except urllib.error.HTTPError as e:
        print(f"[ERROR] SerpApi HTTP {e.code}: {e.reason}")
        return []
    except Exception as e:
        print(f"[ERROR] SerpApi: {e}")
        return []


def search(query: str, engine: str = "tavily", count: int = 5) -> List[Dict]:
    """
    Search the web using the specified engine.

    AI Agent: Engine selection priority:
        DEFAULT ORDER (use unless user specifies):
        1. tavily     - AI-optimized snippets, 1000 free/month (RECOMMENDED)
        2. google     - Complex queries, 100 free/day
        3. brave      - General search, 2000 free/month
        4. duckduckgo - Backup, free, no API key

        ONLY IF EXPLICITLY INSTRUCTED:
        5. serpapi    - Multi-engine, 100 free TOTAL (conserve)
        6. serper     - Fast Google SERP, 2500 free TOTAL (conserve)

    Args:
        query: Search query string
        engine: Engine name (default: tavily)
        count: Number of results (default: 5)

    Returns:
        List of result dicts with title, snippet, url, source
    """
    engine = engine.lower()
    if engine == "google":
        return search_google(query, count)
    elif engine in ("duckduckgo", "ddg"):
        return search_duckduckgo_sync(query, count)
    elif engine == "serper":
        return search_serper(query, count)
    elif engine == "tavily":
        return search_tavily(query, count)
    elif engine == "serpapi":
        return search_serpapi(query, count)
    else:
        return search_brave(query, count)


# =============================================================================
# PERSISTENT STORAGE
# =============================================================================
# AI Agent Note: Use save_results() to persist search results as JSON.
# This avoids console truncation and enables cross-session research tracking.
# Naming: {output_dir}/YYYY-MM-DD/HH-MM[-task-{task}]-{query-slug}.json
# =============================================================================

def slugify(text: str, max_length: int = 40) -> str:
    """
    Convert text to URL-safe slug for filenames.
    Keeps only alphanumeric chars and hyphens, truncates to max_length.
    """
    # Lowercase, replace spaces/underscores with hyphens
    slug = text.lower().strip()
    slug = re.sub(r'[\s_]+', '-', slug)
    # Remove non-alphanumeric except hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Collapse multiple hyphens
    slug = re.sub(r'-+', '-', slug).strip('-')
    # Truncate at word boundary if possible
    if len(slug) > max_length:
        slug = slug[:max_length].rsplit('-', 1)[0]
    return slug or 'search'


def save_results(
    results: List[Dict],
    query: str,
    engine: str,
    output_dir: str,
    task: Optional[str] = None,
    count: int = 5
) -> Path:
    """
    Save search results to organized JSON file.

    AI Agent Usage:
        Prefer this over console output for research workflows.
        Use --task to group related searches (e.g., "seo-research", "competitor-analysis").
        Results include metadata for later analysis and cross-referencing.

    File structure:
        {output_dir}/
        └── 2026-01-19/
            ├── 12-47-task-seo-research-cycling-routes.json
            └── 13-05-hiking-gear-reviews.json

    Returns:
        Path to saved JSON file
    """
    now = datetime.now()
    date_dir = now.strftime('%Y-%m-%d')
    time_prefix = now.strftime('%H-%M-%S')  # Include seconds for uniqueness
    query_slug = slugify(query)

    # Build filename: HH-MM-SS-{engine}[-task-{task}]-{query-slug}.json
    if task:
        filename = f"{time_prefix}-{engine}-task-{slugify(task, 20)}-{query_slug}.json"
    else:
        filename = f"{time_prefix}-{engine}-{query_slug}.json"

    # Create directory structure
    save_dir = Path(output_dir) / date_dir
    save_dir.mkdir(parents=True, exist_ok=True)
    filepath = save_dir / filename

    # Build output with metadata for cross-session tracking
    output = {
        "meta": {
            "query": query,
            "engine": engine,
            "timestamp": now.isoformat(),
            "count_requested": count,
            "count_returned": len(results),
        },
        "results": results
    }

    # Include task if provided (enables grouping/filtering)
    if task:
        output["meta"]["task"] = task

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return filepath


def format_results(results: List[Dict], query: str) -> str:
    """Format search results for display."""
    if not results:
        return f"No results found for '{query}'"

    source = results[0]['source']
    output = [f"\n[SEARCH] Results for: \"{query}\" ({source})\n"]
    output.append("=" * 60)

    for i, r in enumerate(results, 1):
        output.append(f"\n{i}. {r['title']}")

        # For Context7, show library info
        if source == "context7" and r.get("library"):
            output.append(f"   Library: {r['library']}")

        snippet = r['snippet']
        if len(snippet) > 200:
            snippet = snippet[:200] + "..."
        output.append(f"   {snippet}")
        output.append(f"   URL: {r['url']}")

    output.append("\n" + "=" * 60)
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Search the web using multiple search engine APIs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Console output (may truncate in some terminals)
    python web_search.py "how to respond to blog comments"
    python web_search.py "python asyncio tutorial" --count 10 --json

    # Save to JSON file (recommended for AI workflows)
    python web_search.py "best cycling routes NYC" --output searches/
    python web_search.py "seo keywords" -o searches/ --task keyword-research

Engine Priority (AI Agents should follow this order):
    DEFAULT:
    1. tavily     - AI-optimized snippets, 1000 free/month (RECOMMENDED)
    2. google     - Complex queries, 100 free/day
    3. brave      - General search, 2000 free/month
    4. duckduckgo - Backup, free, no API key

    ONLY IF INSTRUCTED:
    5. serpapi    - Multi-engine, 100 free TOTAL
    6. serper     - Fast Google SERP, 2500 free TOTAL

Output Naming Convention:
    {output_dir}/YYYY-MM-DD/HH-MM-SS-{engine}[-task-{task}]-{query-slug}.json
        """
    )

    parser.add_argument("query", help="Search query")
    parser.add_argument("--engine", "-e",
                        choices=["tavily", "google", "brave", "duckduckgo", "ddg",
                                 "serpapi", "serper"],
                        default="tavily",
                        help="Search engine to use (default: tavily)")
    parser.add_argument("--count", "-c", type=int, default=5,
                        help="Number of results (default: 5)")
    parser.add_argument("--json", "-j", action="store_true",
                        help="Output raw JSON to console (use --output for files)")
    # AI Agent: Use --output to avoid console truncation and enable research tracking
    parser.add_argument("--output", "-o", type=str, metavar="DIR",
                        help="Save results as JSON to DIR (organized by date)")
    # AI Agent: Use --task to group related searches for a plan or research session
    parser.add_argument("--task", "-t", type=str, metavar="NAME",
                        help="Tag search with task/plan name (used in filename)")

    args = parser.parse_args()

    results = search(args.query, args.engine, args.count)

    # Save to file if --output specified
    if args.output:
        filepath = save_results(
            results=results,
            query=args.query,
            engine=args.engine,
            output_dir=args.output,
            task=args.task,
            count=args.count
        )
        print(f"[OK] Saved {len(results)} results to: {filepath}")
        # Also print results unless --json specified (for immediate viewing)
        if not args.json:
            print(format_results(results, args.query))
    elif args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_results(results, args.query))


if __name__ == "__main__":
    main()
