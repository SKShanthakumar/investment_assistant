from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph.state import CompiledStateGraph
import json
from pydantic import BaseModel

from src.database.postgres import engine, Base
from src.core.settings import settings
from investment_assistant.graphs import build_research_graph



import json
import aiofiles
from datetime import datetime

LOG_PATH = "logs/langgraph_events.log"

async def log_event(event: dict):
    async with aiofiles.open(LOG_PATH, "a") as f:
        await f.write(
            json.dumps(
                {
                    "ts": datetime.utcnow().isoformat(),
                    "event": event,
                },
                ensure_ascii=False,
                default=str,   # ✅ KEY FIX
            )
            + "\n"
        )




@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Postgres initiated")

    checkpointer_cm = AsyncPostgresSaver.from_conn_string(settings.DB_URI_CHECKPOINTER)
    checkpointer = await checkpointer_cm.__aenter__()
    await checkpointer.setup()

    app.state.checkpointer = checkpointer
    app.state.graph = build_research_graph(checkpointer)

    print("Checkpointer and graph initialized")

    yield

    await checkpointer_cm.__aexit__(None, None, None)
    print("Checkpointer and postgres connection closed")


app = FastAPI(
    title='Investment Assistant',
    lifespan=lifespan
)

class BaseChat(BaseModel):
    thread_id: str

class Chat(BaseChat):
    prompt: str

@app.post('/chat')
async def chat(body: Chat, request: Request):
    graph: CompiledStateGraph = request.app.state.graph
    thread = {"configurable": {"thread_id": body.thread_id}}

    async def event_gen():
        async for event in graph.astream_events(
            {"messages": [body.prompt]},
            config=thread,
        ):
            event_type = event["event"]
            node_name = event.get("metadata", {}).get("langgraph_node")

            if event_type == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content
                if chunk:  # ignore empty chunks
                    yield json.dumps({
                        "type": "token",
                        "content": chunk,
                        "node": node_name
                    }) + "\n"

            elif event_type == "on_chain_stream":
                chunk = event["data"].get("chunk", {})

                if "__interrupt__" in chunk:
                    yield json.dumps({
                        "type": "approval_required",
                        "thread_id": "ui-1"
                    }) + "\n"
                    return  # Stop streaming
                
            elif event_type == "on_chain_end":
                yield json.dumps({
                    "type": "done",
                    "node": node_name
                }) + "\n"

        # End of stream
        yield json.dumps({"type": "stream_end"}) + "\n"        

    return StreamingResponse(event_gen(), media_type="application/json")

class Approve(BaseChat):
    action: bool

@app.post('/approve')
async def approve_research(body: Approve, request: Request):
    graph: CompiledStateGraph = request.app.state.graph
    thread = {"configurable": {"thread_id": body.thread_id}}

    # Check thread already exists
    state = await graph.aget_state(
        config=thread
    )
    if not state[-3]:
        return JSONResponse(content={"message": "Thread not found"}, status_code=400)
    
    # Check whether this thread waits for human approval
    history = [state async for state in graph.aget_state_history(config=thread)]
    next_node = history[0].next
    if next_node and next_node[0] != 'human_approval':
        return JSONResponse(content={"message": "Attempting invalid action"}, status_code=400)
                

    await graph.aupdate_state(config=thread, values={"approved": body.action}, as_node="human_approval")

    async def event_gen():
        async for event in graph.astream_events(
            None,
            config=thread,
        ):
            event_type = event["event"]
            node_name = event.get("metadata", {}).get("langgraph_node")

            await log_event(event)
            if node_name not in ('write_section', 'final_report'):
                continue

            if event_type == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content
                if chunk:  # ignore empty chunks
                    yield json.dumps({
                        "type": "token",
                        "content": chunk,
                        "node": node_name
                    }) + "\n"
                
            elif event_type == "on_chain_end":
                yield json.dumps({
                    "type": "done",
                    "node": node_name
                }) + "\n"
        
        # End of stream
        yield json.dumps({"type": "stream_end"}) + "\n"

    return StreamingResponse(event_gen(), media_type="application/json")