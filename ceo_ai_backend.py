from fastapi import FastAPI, Request
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool

from youtube_publish import publish_to_youtube
from notion_update import update_notion_dashboard

app = FastAPI()

tools = [
    Tool("PublishYouTube", lambda: publish_to_youtube("promo.mp4", "Launch Title", "AI CEO Video", ["AI", "CEO", "automation"]), "Publish a video."),
    Tool("UpdateNotion", lambda: update_notion_dashboard("your_notion_page_id", "CEO.AI published a video and launched products."), "Update dashboard."),
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
    instruction = body.get("command", "")
    result = CEO_AI.run(instruction)
    return {"result": result}
