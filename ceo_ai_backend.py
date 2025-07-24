import re
from fastapi import FastAPI, Request
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool

from youtube_publish import publish_to_youtube
from notion_update import update_notion_dashboard

app = FastAPI()

def parse_command(command):
    # Extract values using basic text matching
    status_match = re.search(r"status[:\-]\s*(.*?)(?:\s+category[:\-]|$)", command, re.IGNORECASE)
    category_match = re.search(r"category[:\-]\s*(.*?)(?:\s+tags[:\-]|$)", command, re.IGNORECASE)
    tags_match = re.search(r"tags[:\-]\s*(.*?)(?:\s+note[:\-]|$)", command, re.IGNORECASE)
    notes_match = re.search(r"note[:\-]\s*(.*)", command, re.IGNORECASE)

    status = status_match.group(1).strip() if status_match else "Update made"
    category = category_match.group(1).strip() if category_match else "General"
    tags = [t.strip() for t in tags_match.group(1).split(",")] if tags_match else ["automation"]
    notes = notes_match.group(1).strip() if notes_match else ""

    return status, category, tags, notes

def get_notion_tool(command):
    page_id = "your_notion_page_id"  # ← Replace this with your actual Notion page ID
    status, category, tags, notes = parse_command(command)
    return lambda: update_notion_dashboard(page_id, status, category, tags, notes)

tools = [
    Tool("PublishYouTube", lambda: publish_to_youtube("promo.mp4", "Launch Title", "AI CEO Video", ["AI", "CEO", "automation"]), "Publish a video."),
    Tool("UpdateNotion", lambda: "Use command: 'status: X category: Y tags: a,b note: Z'", "Update dashboard with structured fields."),
]

llm = OpenAI(model_name="gpt-4", temperature=0.2)
memory = ConversationBufferMemory(memory_key="chat_history")

CEO_AI = initialize_agent(
    tools=tools,
    llm=llm,
    memory=memory,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
)

@app.post("/ceo-ai/run")
async def run_ceo(req: Request):
    body = await req.json()
    command = body.get("command", "")

    if "update notion" in command.lower():
        tool_func = get_notion_tool(command)
        result = tool_func()
        return {"result": f"Notion updated: {result}"}

    result = CEO_AI.run(command)
    return {"result": result}