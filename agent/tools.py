import os
from dotenv import load_dotenv

load_dotenv()

from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from memory import (
    save_fact,
    save_pending_event,
    get_pending_event,
    clear_pending_event,

    save_pending_gmail_email,
    get_pending_gmail_email,
    clear_pending_gmail_email,
)
from calendar_tool import get_upcoming_events, create_calendar_event
from gmail_tool import (
    get_unread_emails,
    search_emails,
    read_email,
    get_emails_for_summary,
    send_email,
    create_email_draft,
)


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

@tool
def gmail_unread_emails() -> str:
    """Get unread emails from the user's Gmail."""
    try:
        return get_unread_emails(5)
    except Exception as e:
        return f"Could not access Gmail: {e}"


@tool
def gmail_search(query: str) -> str:
    """Search the user's Gmail using a Gmail search query."""
    try:
        return search_emails(query, 5)
    except Exception as e:
        return f"Could not search Gmail: {e}"


@tool
def gmail_read_email(message_id: str) -> str:
    """Read the content of a specific Gmail email using its message ID."""
    try:
        return read_email(message_id)
    except Exception as e:
        return f"Could not read email: {e}"


@tool
def gmail_send_email(
    to: str,
    subject: str,
    body: str
) -> str:
    """
    Prepare an email for confirmation.
    Does not send the email immediately.
    """

    try:
        save_pending_gmail_email(
            to,
            subject,
            body
        )

        return (
            f"Email prepared successfully.\n"
            f"To: {to}\n"
            f"Subject: {subject}\n"
            f"Ask the user for confirmation before sending."
        )

    except Exception as e:
        return f"Could not prepare email: {e}"


@tool
def gmail_confirm_send_email(
    confirmation: str
) -> str:
    """
    Send the pending Gmail email after explicit confirmation.
    """

    confirmation = confirmation.lower().strip()

    pending_email = get_pending_gmail_email()

    if not pending_email:
        return "There is no pending email."

    if confirmation in [
        "yes",
        "y",
        "confirm",
        "confirmed",
        "yes please",
        "send it",
        "send",
        "haan",
        "ha",
        "bhej do"
    ]:

        to, subject, body = pending_email

        try:
            result = send_email(
                to,
                subject,
                body
            )

            clear_pending_gmail_email()

            return result

        except Exception as e:
            return f"Could not send email: {e}"

    if confirmation in [
        "no",
        "n",
        "cancel",
        "cancel it",
        "nahi",
        "mat bhejo"
    ]:

        clear_pending_gmail_email()

        return "Email cancelled."

    return "Please say yes to send the email or no to cancel."


@tool
def gmail_create_draft(
    to: str,
    subject: str,
    body: str
) -> str:
    """Create a Gmail draft without sending it."""
    try:
        return create_email_draft(to, subject, body)
    except Exception as e:
        return f"Could not create Gmail draft: {e}"


@tool
def gmail_summarize_emails() -> str:
    """Get recent emails so the AI agent can summarize them."""
    try:
        return get_emails_for_summary(5)
    except Exception as e:
        return f"Could not retrieve emails for summary: {e}"