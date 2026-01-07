from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
import json

from src.schemas import Chat, Approve
from src.services import chat as chat_service

router = APIRouter()

@router.post('/')
async def chat(body: Chat, request: Request):
    stream_generator = await chat_service.chat(request.app.state.graph, body.thread_id, body.prompt)

    return StreamingResponse(stream_generator(), media_type="application/json")


@router.post('/approve')
async def approve_research(body: Approve, request: Request):
    # service returns either 'error', error_message or 'success', stream_generator
    result, return_object = await chat_service.approve_research(request.app.state.graph, body.thread_id, body.action)

    if result == "error":
        return JSONResponse(content=return_object, status_code=400)

    return StreamingResponse(return_object(), media_type="application/json")
