from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.graph.state import CompiledStateGraph

from app.core.config import settings
from app.routes import chat_router
from investment_assistant.graphs import build_research_graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    with MongoDBSaver.from_conn_string(conn_string=settings.MONGODB_URI, db_name='investment_assistant') as checkpointer:

        app.state.graph = build_research_graph(checkpointer)
        print("Checkpointer and graph initialized")

        yield

    print("App shutdown completed")


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
