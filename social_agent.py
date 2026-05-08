from tavily import TavilyClient
import config

client = TavilyClient(api_key=config.TAVILY_API_KEY)

PLATFORMS = {
    "Twitter/X":  "site:twitter.com OR site:x.com",
    "Instagram":  "site:instagram.com",
    "LinkedIn":   "site:linkedin.com",
    "GitHub":     "site:github.com",
    "YouTube":    "site:youtube.com",
    "Reddit":     "site:reddit.com",
}

def find_accounts(name: str) -> dict:
    """Find public social accounts for a name or username. Ethical use only."""
    found = {}
    for platform, site_filter in PLATFORMS.items():
        try:
            response = client.search(query=f"{site_filter} {name}", max_results=2)
            for r in response.get("results", []):
                url = r.get("url", "").lower()
                if name.lower().replace(" ", "") in url or name.lower() in url:
                    found[platform] = {
                        "url":     r.get("url"),
                        "title":   r.get("title"),
                        "snippet": r.get("content", "")[:150]
                    }
                    break
        except Exception:
            pass
    return found

def format_accounts(results: dict) -> str:
    if not results:
        return "No public accounts found for that name."
    lines = [f"Found {len(results)} public account(s):\n"]
    for platform, data in results.items():
        lines.append(f"✅ {platform}: {data['url']}")
    lines.append("\n⚠️ Only public accounts shown. Use ethically.")
    return "\n".join(lines)
