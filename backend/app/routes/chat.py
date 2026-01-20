from fastapi import APIRouter, Request, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services import chat as chat_service
from app.database.mongo import get_mongo_db

router = APIRouter()

@router.get('/approve')
async def approve_research(action: bool, thread_id: str, request: Request, background_tasks: BackgroundTasks, db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    
    # service returns either 'error', error_message or 'success', stream_generator
    result, return_object = await chat_service.approve_research(request.app.state.graph, thread_id, action, background_tasks, db)

    if result == "error":
        return JSONResponse(content=return_object, status_code=400)

    return StreamingResponse(
        return_object(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get('/list/{thread_id}', response_class=JSONResponse)
async def get_chat_list(thread_id: str, db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    return await chat_service.get_chat_list(thread_id, db)


@router.get('/history', response_class=JSONResponse)
async def get_chat_history(db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    return await chat_service.get_chat_history(db)


@router.get('/')
async def chat(prompt: str, request: Request, background_tasks: BackgroundTasks, db: AsyncIOMotorDatabase = Depends(get_mongo_db), thread_id: str = None):

    stream_generator = await chat_service.chat(request.app.state.graph, thread_id, prompt, background_tasks, db)

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
