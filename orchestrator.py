from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
import re

from web_agent    import web_search, format_search_results
from social_agent import find_accounts, format_accounts
from judge_agent  import get_best_answer
from vector_store import save_memory, recall_memory

class ButlerState(TypedDict):
    command:        str
    needs_web:      bool
    needs_social:   bool
    needs_teaching: bool
    web_data:       str
    social_data:    str
    memories:       List[dict]
    final_answer:   str
    error:          Optional[str]

def analyze(state: ButlerState) -> ButlerState:
    cmd = state["command"].lower()
    state["needs_web"]      = any(k in cmd for k in ["search","find","what is","how","explain","teach","learn","latest","who","tell me","research"])
    state["needs_social"]   = any(k in cmd for k in ["account","profile","social","instagram","twitter","github","find person","username"])
    state["needs_teaching"] = any(k in cmd for k in ["teach","explain","how does","what is","learn","understand","show me"])
    return state

def get_mem(state: ButlerState) -> ButlerState:
    try:
        state["memories"] = recall_memory(state["command"], top_k=4)
    except Exception:
        state["memories"] = []
    return state

def do_web(state: ButlerState) -> ButlerState:
    if state["needs_web"]:
        result = web_search(state["command"])
        state["web_data"] = format_search_results(result)
    else:
        state["web_data"] = ""
    return state

def do_social(state: ButlerState) -> ButlerState:
    if not state["needs_social"]:
        state["social_data"] = ""
        return state
    match = re.search(r"(?:find|search for|look up)\s+([A-Za-z0-9_\s]+?)(?:'s|\s+account|\s+profile|$)", state["command"], re.IGNORECASE)
    name = match.group(1).strip() if match else None
    if name:
        state["social_data"] = format_accounts(find_accounts(name))
    else:
        state["social_data"] = "Please say: 'find [name] accounts'"
    return state

def synthesize(state: ButlerState) -> ButlerState:
    context_parts = []
    if state["memories"]:
        mem_text = "\n".join(f"- {m['text'][:200]}" for m in state["memories"][:3])
        context_parts.append(f"Past memories:\n{mem_text}")
    if state["web_data"]:
        context_parts.append(f"Web results:\n{state['web_data']}")
    if state["social_data"]:
        context_parts.append(f"Social search:\n{state['social_data']}")
    if state["needs_teaching"]:
        context_parts.append("Teach step by step: WHY → WHAT → HOW → practical example → ask for doubts")
    result = get_best_answer(state["command"], "\n\n".join(context_parts))
    state["final_answer"] = result["master"]
    return state

def store_mem(state: ButlerState) -> ButlerState:
    try:
        save_memory(f"Q: {state['command']}\nA: {state['final_answer'][:400]}")
    except Exception:
        pass
    return state

def build_butler():
    g = StateGraph(ButlerState)
    g.add_node("analyze",    analyze)
    g.add_node("get_mem",    get_mem)
    g.add_node("do_web",     do_web)
    g.add_node("do_social",  do_social)
    g.add_node("synthesize", synthesize)
    g.add_node("store_mem",  store_mem)
    g.set_entry_point("analyze")
    g.add_edge("analyze",    "get_mem")
    g.add_edge("get_mem",    "do_web")
    g.add_edge("do_web",     "do_social")
    g.add_edge("do_social",  "synthesize")
    g.add_edge("synthesize", "store_mem")
    g.add_edge("store_mem",  END)
    return g.compile()

butler = build_butler()

def run(command: str) -> str:
    result = butler.invoke({
        "command": command, "needs_web": False, "needs_social": False,
        "needs_teaching": False, "web_data": "", "social_data": "",
        "memories": [], "final_answer": "", "error": None
    })
    return result["final_answer"]
