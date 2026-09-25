import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent

from agent.tools import (
    calculator,
    tavily_search,
    remember_fact,
    calendar_events,
    create_calendar_event_tool,
    confirm_calendar_event,

    gmail_unread_emails,
    gmail_search,
    gmail_read_email,
    gmail_send_email,
    gmail_confirm_send_email,
    gmail_create_draft,
    gmail_summarize_emails,
)

from memory import (
    get_recent_messages,
    get_facts,
    get_pending_event,
    get_pending_gmail_email,
)


load_dotenv()


# =========================================================
# LLM
# =========================================================

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
)


# =========================================================
# TOOLS
# =========================================================

tools = [
    calculator,
    tavily_search,
    remember_fact,

    calendar_events,
    create_calendar_event_tool,
    confirm_calendar_event,

    gmail_unread_emails,
    gmail_search,
    gmail_read_email,
    gmail_send_email,
    gmail_confirm_send_email,
    gmail_create_draft,
    gmail_summarize_emails,
]


# =========================================================
# AGENT
# =========================================================

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""

You are a concise voice assistant.

Keep your answers short and conversational.
Usually answer in 1 to 3 sentences.

Do not give long explanations unless the user explicitly asks for details.

Avoid markdown tables, long lists, and lengthy roadmaps.

Your response will be converted to speech,
so make it natural and easy to listen to.


=========================================================
MEMORY RULES
=========================================================

When the user tells you a stable personal fact about themselves,
you MUST call the remember_fact tool before answering.

Examples of facts that should be remembered:

- "My name is Priyanshu."
- "I am learning LangChain."
- "I am learning AI agent development."
- "My favorite programming language is Python."
- "I like Python."

Do NOT use the tool for:

- questions
- temporary information
- general knowledge
- facts about other people
- facts about the world

Only save information explicitly stated by the user.

Do not save sensitive personal information unless the user
explicitly asks you to remember it.


=========================================================
CALENDAR CONFIRMATION RULES
=========================================================

When there is a pending calendar event and the user says:

"yes"
"confirm"
"confirmed"
"okay"

or similar confirmation,

you MUST call the confirm_calendar_event tool.

Do not answer the confirmation request using remembered facts
or conversation history.

If the user says:

"no"
"cancel"

or similar,

you MUST call confirm_calendar_event with the cancellation.


For a new calendar event:

1. First use create_calendar_event_tool to save it as pending.
2. Then ask the user for confirmation.
3. Never create the Google Calendar event before confirmation.

=========================================================
GMAIL CONFIRMATION RULES
=========================================================

When the user wants to send an email:

1. First use gmail_send_email.
2. Never send the email immediately.
3. Ask the user for confirmation.

If the user confirms with:
"yes"
"confirm"
"send it"
"haan"
"bhej do"

the email must be sent using gmail_confirm_send_email.

If the user says:
"no"
"cancel"
"nahi"
"mat bhejo"

cancel the pending email.

Never send an email without explicit confirmation.

"""
)


# =========================================================
# LAST TOOL USED
# =========================================================

LAST_TOOL_USED = None


def get_last_tool_used():
    """
    Return the tool used during the latest request.
    """

    return LAST_TOOL_USED


# =========================================================
# TOOL DETECTION
# =========================================================

def detect_tool(tool_name):

    global LAST_TOOL_USED

    if tool_name == "calculator":

        LAST_TOOL_USED = "Calculator"

    elif tool_name == "tavily_search":

        LAST_TOOL_USED = "Web Search"

    elif tool_name == "remember_fact":

        LAST_TOOL_USED = "Memory"

    elif tool_name in [
        "calendar_events",
        "create_calendar_event_tool",
        "confirm_calendar_event"
    ]:

        LAST_TOOL_USED = "Google Calendar"

    elif tool_name in [
    "gmail_unread_emails",
    "gmail_search",
    "gmail_read_email",
    "gmail_send_email",
    "gmail_confirm_send_email",
    "gmail_create_draft",
    "gmail_summarize_emails"
    ]:
        LAST_TOOL_USED = "Gmail"


# =========================================================
# GET RESPONSE
# =========================================================

def get_response(text):

    global LAST_TOOL_USED

    # Reset previous tool
    LAST_TOOL_USED = None


    # =====================================================
    # 1. CHECK PENDING CALENDAR CONFIRMATION
    # =====================================================

    pending_event = get_pending_event()


    if pending_event:

        command = text.lower().strip()

        command = (
            command
            .replace(".", "")
            .replace("!", "")
            .replace("?", "")
        )


        # ---------------------------------------------
        # YES / CONFIRM
        # ---------------------------------------------

        yes_words = [
            "yes",
            "yes confirm",
            "yes confirm it",
            "confirm",
            "confirm it",
            "ok",
            "okay",
            "haan",
            "ha",
            "kar do",
            "yes please"
        ]


        # ---------------------------------------------
        # NO / CANCEL
        # ---------------------------------------------

        no_words = [
            "no",
            "cancel",
            "cancel it",
            "don't",
            "nahi",
            "mat karo"
        ]


        # ---------------------------------------------
        # USER CONFIRMED
        # ---------------------------------------------

        if command in yes_words:

            LAST_TOOL_USED = "Google Calendar"

            result = confirm_calendar_event.invoke({
                "confirmation": "yes"
            })

            return result


        # ---------------------------------------------
        # USER CANCELLED
        # ---------------------------------------------

        if command in no_words:

            LAST_TOOL_USED = "Google Calendar"

            result = confirm_calendar_event.invoke({
                "confirmation": "no"
            })

            return result


    # =====================================================
    # 2. NORMAL AGENT WORKFLOW
    # =====================================================

    stored_messages = get_recent_messages(10)

    facts = get_facts()

    messages = []

    pending_gmail = get_pending_gmail_email()

    if pending_gmail:
        command = text.lower().strip()

        command = (
            command
            .replace(".", "")
            .replace("!", "")
            .replace("?", "")
            .replace(",", "")
        )

        yes_words = [
        "yes",
        "y",
        "confirm",
        "confirmed",
        "yes please",
        "yes send it",
        "send it",
        "send",
        "haan",
        "ha",
        "bhej do"
    ]

        no_words = [
            "no",
            "n",
            "cancel",
            "cancel it",
            "nahi",
            "mat bhejo"
        ]

        if command in yes_words:
            LAST_TOOL_USED = "Gmail"

            result = gmail_confirm_send_email.invoke({
                "confirmation": "yes"
            })

            return result

        if command in no_words:
            LAST_TOOL_USED = "Gmail"

            result = gmail_confirm_send_email.invoke({
                "confirmation": "no"
            })

            return result




    # =====================================================
    # ADD REMEMBERED FACTS
    # =====================================================

    if facts:

        facts_text = "\n".join(
            f"- {fact}"
            for fact in facts
        )


        messages.append({

            "role": "system",

            "content": f"""
These are important facts remembered about the user:

{facts_text}

Use these facts when relevant.

Do not mention the memory system unless the user asks.
"""

        })


    # =====================================================
    # ADD RECENT CONVERSATION
    # =====================================================

    for role, message in stored_messages:

        messages.append({

            "role": role,

            "content": message

        })


    # =====================================================
    # ADD CURRENT USER MESSAGE
    # =====================================================

    messages.append({

        "role": "user",

        "content": text

    })


    # =====================================================
    # 3. RUN LANGCHAIN AGENT
    # =====================================================

    result = agent.invoke({

        "messages": messages

    })


    # =====================================================
    # 4. DETECT TOOL USED
    # =====================================================

    for message in result["messages"]:

        tool_calls = getattr(
            message,
            "tool_calls",
            []
        )


        if tool_calls:

            for tool_call in tool_calls:

                tool_name = tool_call.get(
                    "name",
                    ""
                )

                detect_tool(tool_name)


    # =====================================================
    # 5. EXTRACT FINAL RESPONSE
    # =====================================================

    content = result["messages"][-1].content


    if isinstance(content, list):

        response = content[0]["text"]

    else:

        response = content


    # =====================================================
    # 6. RETURN RESPONSE
    # =====================================================

    return response