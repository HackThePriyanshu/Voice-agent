from langchain_core.tools import tool
from langchain_tavily import TavilySearch


@tool
def calculator(expression: str) -> str:
    """Calculate a mathematical expression."""

    try:
        result = eval(expression)
        return str(result)
    except Exception:
        return "Invalid mathematical expression."


tavily_search = TavilySearch(
    max_results=3
)

from memory import save_fact

@tool
def remember_fact(fact: str) -> str:
    """Save a stable and useful fact about the user for future conversations."""
    print("🧠 REMEMBER FACT TOOL CALLED:", fact)

    save_fact(fact)

    return "Fact saved successfully."