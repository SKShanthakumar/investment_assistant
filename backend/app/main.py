from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph.state import CompiledStateGraph

from app.database.postgres import engine, Base
from app.core.config import settings
from app.routes import chat_router
from investment_assistant.graphs import build_research_graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Postgres initiated")

    checkpointer_manager = AsyncPostgresSaver.from_conn_string(settings.DB_URI_CHECKPOINTER)
    checkpointer = await checkpointer_manager.__aenter__()
    await checkpointer.setup()

    app.state.graph = build_research_graph(checkpointer)

    print("Checkpointer and graph initialized")

    yield

    await checkpointer_manager.__aexit__(None, None, None)
    print("Checkpointer and postgres connection closed")


app = FastAPI(
    title='Investment Assistant',
    lifespan=lifespan
)

app.include_router(chat_router, prefix='/chat')

origins = ['http://localhost:5173']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/test')
async def test(request: Request):
    graph: CompiledStateGraph = request.app.state.graph
    thread = {"configurable": {"thread_id": '22113'}}

    return await graph.aget_state(config=thread)