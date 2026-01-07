from fastapi import FastAPI
from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph.state import CompiledStateGraph

from src.database.postgres import engine, Base
from src.core.settings import settings
from src.routes import chat_router
from investment_assistant.graphs import build_research_graph


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

app.include_router(chat_router, prefix='/chat')
