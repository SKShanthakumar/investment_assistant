from langgraph.graph.state import CompiledStateGraph    
import json

from app.utils.chat import validate_thread

async def chat(graph: CompiledStateGraph, thread_id: str, prompt: str):
    thread = {"configurable": {"thread_id": thread_id}}

    async def event_gen():
        async for event in graph.astream_events(
            {"messages": [prompt]},
            config=thread,
        ):
            event_type = event["event"]
            node_name = event.get("metadata", {}).get("langgraph_node")
            
            # Chat model streaming tokens
            if event_type == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content

                if chunk:  # ignore empty chunks
                    yield f'data: {json.dumps({
                        "type": "token",
                        "content": chunk,
                        "node": node_name
                    })}' + "\n\n"

            # Token to notify human approval required
            elif event_type == "on_chain_stream":
                chunk = event["data"].get("chunk", {})

                if "__interrupt__" in chunk:
                    yield f'data: {json.dumps({
                        "type": "approval_required",
                        "thread_id": "ui-1"
                    })}' + "\n\n"

                    return  # Stop streaming
            
            # Token to notify end of node processing
            elif event_type == "on_chain_end":
                yield f'data: {json.dumps({
                    "type": "done",
                    "node": node_name
                })}'+ "\n\n"

        # End of stream
        yield f'data: {json.dumps({"type": "stream_end"})}' + "\n\n"     

    return event_gen

async def approve_research(graph: CompiledStateGraph, thread_id: str, action: bool):
    thread = {"configurable": {"thread_id": thread_id}}

    if not validate_thread(graph, thread):
        return "error", {"message": "Invalid thread id."}

    # Update state with approval action
    await graph.aupdate_state(config=thread, values={"approved": action}, as_node="human_approval")

    async def event_gen():
        async for event in graph.astream_events(
            None,
            config=thread,
        ):
            event_type = event["event"]
            node_name = event.get("metadata", {}).get("langgraph_node")

            if node_name not in ('write_analysis_report', 'final_report'):
                continue
            
            # Chat model streaming tokens
            if event_type == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content
                if chunk:  # ignore empty chunks
                    yield f'data: {json.dumps({
                        "type": "token",
                        "content": chunk,
                        "node": node_name
                    })}' + "\n\n"
            
            # Token to notify end of node processing
            elif event_type == "on_chain_end":
                yield f'data: {json.dumps({
                    "type": "done",
                    "node": node_name
                })}' + "\n\n"
        
        # End of stream
        yield f'data: {json.dumps({"type": "stream_end"})}' + "\n\n"

    return "success", event_gen
