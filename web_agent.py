from tavily import TavilyClient
import config

client = TavilyClient(api_key=config.TAVILY_API_KEY)

def web_search(query: str, max_results: int = 5) -> dict:
    try:
        response = client.search(
            query=query, max_results=max_results,
            search_depth="advanced", include_answer=True
        )
        sources = []
        for r in response.get("results", []):
            sources.append({
                "title":   r.get("title", ""),
                "url":     r.get("url", ""),
                "snippet": r.get("content", "")[:400]
            })
        return {"answer": response.get("answer", ""), "sources": sources}
    except Exception as e:
        return {"answer": f"Search error: {e}", "sources": []}

def format_search_results(result: dict) -> str:
    parts = []
    if result.get("answer"):
        parts.append(f"Answer: {result['answer']}")
    for s in result.get("sources", [])[:3]:
        if s["snippet"]:
            parts.append(f"[{s['title']}]: {s['snippet']}")
    return "\n\n".join(parts)
