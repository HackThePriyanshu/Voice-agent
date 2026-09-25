import os
from dotenv import load_dotenv

load_dotenv()

from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from memory import (
    save_fact,
    save_pending_event,
    get_pending_event,
    clear_pending_event
)
from calendar_tool import get_upcoming_events, create_calendar_event


@tool
def calculator(expression: str) -> str:
    """Calculate a mathematical expression."""
    try:
        result = eval(expression)
        return str(result)
    except Exception:
        return "Invalid mathematical expression."


tavily_search = TavilySearch(
    max_results=3,
    tavily_api_key=os.getenv("TAVILY_API_KEY")
)


@tool
def remember_fact(fact: str) -> str:
    """Save a stable and useful fact about the user for future conversations."""
    print("🧠 REMEMBER FACT TOOL CALLED:", fact)
    save_fact(fact)
    return "Fact saved successfully."


@tool
def calendar_events() -> str:
    """Check the user's upcoming Google Calendar events."""
    try:
        return get_upcoming_events(10)
    except Exception as e:
        return f"Could not access Google Calendar: {e}"

@tool
def create_calendar_event_tool(
    summary: str,
    start_datetime: str,
    end_datetime: str
) -> str:
    """
    Prepare a calendar event for confirmation.
    Does not create the event immediately.
    """

    try:
        save_pending_event(
            summary,
            start_datetime,
            end_datetime
        )

        return (
            f"Pending calendar event: {summary}, "
            f"from {start_datetime} to {end_datetime}. "
            f"Ask the user for confirmation before creating it."
        )

    except Exception as e:
        return f"Could not prepare calendar event: {e}"

@tool
def confirm_calendar_event(confirmation: str) -> str:
    """
    Confirm or reject the pending calendar event.
    """

    confirmation = confirmation.lower().strip()

    pending_event = get_pending_event()

    if not pending_event:
        return "There is no pending calendar event."

    if confirmation in [
        "yes",
        "y",
        "yes please",
        "confirm",
        "confirmed",
        "okay",
        "ok"
    ]:
        summary, start_datetime, end_datetime = pending_event

        try:
            result = create_calendar_event(
                summary,
                start_datetime,
                end_datetime
            )

            clear_pending_event()

            return (
                f"Calendar event created successfully. "
                f"Title: {result['summary']}. "
                f"Start: {result['start']}."
            )

        except Exception as e:
            return f"Could not create calendar event: {e}"

    elif confirmation in [
        "no",
        "n",
        "cancel",
        "cancel it",
        "don't"
    ]:
        clear_pending_event()
        return "Calendar event cancelled."

    return "Please say yes to confirm or no to cancel."