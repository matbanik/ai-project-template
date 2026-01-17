#!/usr/bin/env python3
"""
Web Search Tool
===============
Search the web using Google Custom Search, Brave Search, or Context7 APIs.

Usage:
    python web_search.py "your search query"
    python web_search.py "your query" --engine brave
    python web_search.py "your query" --engine google
    python web_search.py "your query" --engine context7
    python web_search.py "how to use pandas dataframe" --engine context7
    python web_search.py "your query" --count 10

Requirements:
    pip install requests

APIs (configured in api-keys.json):
    - Google Custom Search: 100 free queries/day
    - Brave Search: 2000 free queries/month
    - Context7: Code documentation and library search
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import urllib.request
import urllib.parse
import urllib.error


def load_api_keys() -> Dict:
    """Load API keys from api-keys.json."""
    api_keys_path = Path(__file__).parent.parent / "api-keys.json"
    if not api_keys_path.exists():
        print(f"❌ API keys file not found: {api_keys_path}")
        sys.exit(1)

    with open(api_keys_path, "r", encoding="utf-8") as f:
        return json.load(f)


def search_google(query: str, count: int = 5) -> List[Dict]:
    """Search using Google Custom Search API."""
    keys = load_api_keys()

    if "google_search" not in keys:
        print("❌ Google Search not configured in api-keys.json")
        return []

    api_key = keys["google_search"]["api_key"]
    cse_id = keys["google_search"]["cse_id"]

    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={urllib.parse.quote(query)}&num={min(count, 10)}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())

        if "error" in data:
            print(f"❌ Google API Error: {data['error']['message']}")
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
        print(f"❌ HTTP Error: {e.code} - {e.reason}")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def search_brave(query: str, count: int = 5) -> List[Dict]:
    """Search using Brave Search API."""
    keys = load_api_keys()

    if "brave_search" not in keys:
        print("❌ Brave Search not configured in api-keys.json")
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
        print(f"❌ HTTP Error: {e.code} - {e.reason}")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def search_context7(query: str, count: int = 5) -> List[Dict]:
    """
    Context7 MCP server for code documentation.

    Context7 is an MCP (Model Context Protocol) server - it doesn't have a REST API.
    It's designed for AI code editors like Cursor, Windsurf, VS Code with Cline, etc.

    To use Context7:
    1. Add to your AI editor's MCP settings:
       {
         "context7": {
           "type": "http",
           "url": "https://context7.liam.sh/mcp"
         }
       }
    2. In your AI prompt, include "use context7" to activate it

    For CLI usage, use --engine brave or --engine google instead.
    """
    print("ℹ️  Context7 is an MCP server (not a REST API)")
    print("   It's designed for AI code editors, not CLI scripts.")
    print("")
    print("   To use Context7 in your AI editor:")
    print("   1. Add to mcp_settings.json:")
    print('      "context7": { "type": "http", "url": "https://context7.liam.sh/mcp" }')
    print("   2. Use 'use context7' in your AI prompts")
    print("")
    print("   For CLI search, try: --engine brave or --engine google")

    return []


def search(query: str, engine: str = "brave", count: int = 5) -> List[Dict]:
    """
    Search the web using the specified engine.

    Args:
        query: Search query string
        engine: 'brave', 'google', or 'context7' (default: brave)
        count: Number of results (default: 5)

    Returns:
        List of result dicts with title, snippet, url, source
    """
    engine = engine.lower()
    if engine == "google":
        return search_google(query, count)
    elif engine == "context7":
        return search_context7(query, count)
    else:
        return search_brave(query, count)


def format_results(results: List[Dict], query: str) -> str:
    """Format search results for display."""
    if not results:
        return f"No results found for '{query}'"

    source = results[0]['source']
    output = [f"\n🔍 Search results for: \"{query}\" ({source})\n"]
    output.append("=" * 60)

    for i, r in enumerate(results, 1):
        output.append(f"\n{i}. {r['title']}")

        # For Context7, show library info
        if source == "context7" and r.get("library"):
            output.append(f"   📚 Library: {r['library']}")

        snippet = r['snippet']
        if len(snippet) > 200:
            snippet = snippet[:200] + "..."
        output.append(f"   {snippet}")
        output.append(f"   🔗 {r['url']}")

    output.append("\n" + "=" * 60)
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Search the web using Google, Brave, or Context7 APIs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python web_search.py "how to respond to blog comments"
    python web_search.py "best cycling routes NYC" --engine google
    python web_search.py "how to use pandas dataframe" --engine context7
    python web_search.py "python asyncio tutorial" --count 10 --json
        """
    )

    parser.add_argument("query", help="Search query")
    parser.add_argument("--engine", "-e", choices=["brave", "google", "context7"], default="brave",
                        help="Search engine to use (default: brave)")
    parser.add_argument("--count", "-c", type=int, default=5,
                        help="Number of results (default: 5)")
    parser.add_argument("--json", "-j", action="store_true",
                        help="Output raw JSON instead of formatted text")

    args = parser.parse_args()

    results = search(args.query, args.engine, args.count)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_results(results, args.query))


if __name__ == "__main__":
    main()
