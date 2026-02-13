from langgraph.graph.state import CompiledStateGraph
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
import json
import uuid

from app.utils.chat import validate_thread


async def add_chat_to_db(thread_id: str, role: str, message: str, db: AsyncIOMotorDatabase):
    """ Background task to add chat list to mongodb """

    chat_doc = {
        "role": role,
        "message": message
    }

    await db.chat.update_one(
        {"thread_id": thread_id},
        {
            "$push": {"chat": chat_doc},
            "$setOnInsert": {"thread_id": thread_id}
        },
        upsert=True
    )


async def chat(graph: CompiledStateGraph, thread_id: str, prompt: str, background_tasks: BackgroundTasks, db: AsyncIOMotorDatabase):
    """ Main chat endpoint """
    
    if thread_id is None:
        # New chat
        thread_id = str(uuid.uuid4())
    thread = {"configurable": {"thread_id": thread_id}}

    background_tasks.add_task(add_chat_to_db, thread_id, 'user', prompt, db)

    async def event_gen():
        message_chunks = []

        async for event in graph.astream_events({"messages": [prompt]}, config=thread):
            event_type = event["event"]
            node_name = event.get("metadata", {}).get("langgraph_node")

            # Chat model streaming tokens
            if event_type == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content

                if chunk:  # ignore empty chunks
                    message_chunks.append(chunk)

                    yield f'data: {json.dumps({
                        "type": "token",
                        "content": chunk,
                        "node": node_name
                    })}' + "\n\n"

            # Catch interrupt and custom stream
            elif event_type == "on_chain_stream":
                chunk = event["data"].get("chunk", {})

                if "__interrupt__" in chunk:
                    yield f'data: {json.dumps({
                        "type": "approval_required",
                        "thread_id": thread_id
                    })}' + "\n\n"
                    
                    background_tasks.add_task(add_chat_to_db, thread_id, 'ai', ''.join(message_chunks), db)

                    return  # Stop streaming
                
                if chunk and event['name'] == 'fake_stream':
                    message_chunks.append(chunk)

                    yield f'data: {json.dumps({
                        "type": "token",
                        "content": chunk,
                        "node": node_name
                    })}' + "\n\n"

        background_tasks.add_task(add_chat_to_db, thread_id, 'ai', ''.join(message_chunks), db)

        # End of stream
        yield f'data: {json.dumps({"type": "stream_end", "thread_id": thread_id})}' + "\n\n"     
    
    return event_gen


async def approve_research(graph: CompiledStateGraph, thread_id: str, action: bool, background_tasks: BackgroundTasks, db: AsyncIOMotorDatabase):
    """ Starts deep research on user approval. resumes graph on human approval node """
    
    thread = {"configurable": {"thread_id": thread_id}}

    if not await validate_thread(graph, thread):
        return "error", {"message": "Invalid thread id."}

    # Update state with approval action
    await graph.aupdate_state(config=thread, values={"approved": action}, as_node="human_approval")

    background_tasks.add_task(add_chat_to_db, thread_id, 'user', 'Approve' if action else 'Reject', db)

    async def event_gen():
        message_chunks = []

        async for event in graph.astream_events(None, config=thread):
            event_type = event["event"]
            node_name = event.get("metadata", {}).get("langgraph_node")

            if node_name not in ('write_analysis_report', 'final_report'):
                # Need not stream agent interview, only report should be streamed to user
                continue
            
            # Chat model streaming tokens
            if event_type == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content

                if chunk:
                    message_chunks.append(chunk)

                    yield f'data: {json.dumps({
                        "type": "token",
                        "content": chunk,
                        "node": node_name,
                    })}' + "\n\n"
            
            # Token to notify end of node processing, used in UI to separate analysis reports and final report
            elif event_type == "on_chain_end":
                if node_name == 'write_analysis_report':
                    message_chunks.append('\n\n---\n\n')    # Separation of reports

                yield f'data: {json.dumps({
                    "type": "done",
                    "node": node_name
                })}' + "\n\n"
        
        background_tasks.add_task(add_chat_to_db, thread_id, 'ai', ''.join(message_chunks), db)

        # End of stream
        yield f'data: {json.dumps({"type": "stream_end", "thread_id": thread_id})}' + "\n\n"

    return "success", event_gen


async def get_chat_list(thread_id: str, db: AsyncIOMotorDatabase):
    """ Gets previous messages of a thread """

    result = await db.chat.find_one({"thread_id": thread_id})
    return JSONResponse(content={'chat': result['chat']})


async def get_chat_history(db: AsyncIOMotorDatabase):
    """ List of chat history """
    
    docs = []
    async for doc in db.chat.find({}):
        docs.append({
            'thread_id': doc['thread_id'],
            'title': doc['chat'][0]['message']
        })
    return JSONResponse(content={'history': docs[::-1]})
