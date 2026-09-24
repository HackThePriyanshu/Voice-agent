import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent

from agent.tools import calculator, tavily_search, remember_fact
from memory import get_recent_messages, get_facts

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
)

tools = [calculator, tavily_search, remember_fact]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""

    You are a concise voice assistant.

    Keep your answers short and conversational.
    Usually answer in 1 to 3 sentences.
    Do not give long explanations unless the user explicitly asks for details.
    Avoid markdown tables, long lists, and lengthy roadmaps.
    Your response will be converted to speech, so make it natural and easy to listen to.

    When the user tells you a stable personal fact about themselves, you MUST call the remember_fact tool before answering.

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
    Do not save sensitive personal information unless the user explicitly asks you to remember it.
    """
)



def get_response(text):

    # Recent conversation
    stored_messages = get_recent_messages(10)

    # Long-term facts
    facts = get_facts()

    messages = []

    # Important facts ko system context ke through dena
    if facts:
        facts_text = "\n".join(f"- {fact}" for fact in facts)

        messages.append({
            "role": "system",
            "content": f"""
These are important facts remembered about the user:

{facts_text}

Use these facts when relevant. Do not mention the memory system unless the user asks.
"""
        })

    # Recent conversation
    for role, message in stored_messages:
        messages.append({
            "role": role,
            "content": message
        })

    # Current question
    messages.append({
        "role": "user",
        "content": text
    })

    result = agent.invoke(
        {
            "messages": messages
        }
    )

    content = result["messages"][-1].content

    if isinstance(content, list):
        response = content[0]["text"]
    else:
        response = content

    return response