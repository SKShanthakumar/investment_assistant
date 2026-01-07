from langgraph.graph.state import CompiledStateGraph
import json

async def chat(graph: CompiledStateGraph, thread_id: str, prompt: str):
    thread = {"configurable": {"thread_id": thread_id}}

    async def event_gen():
        async for event in graph.astream_events(
            {"messages": [prompt]},
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

    return event_gen

async def approve_research(graph: CompiledStateGraph, thread_id: str, action: bool):
    thread = {"configurable": {"thread_id": thread_id}}

    # Check thread already exists
    state = await graph.aget_state(
        config=thread
    )
    if not state[-3]:
        return "error", {"message": "Thread not found"}
    
    # Check whether this thread waits for human approval
    history = [state async for state in graph.aget_state_history(config=thread)]
    next_node = history[0].next
    if not next_node or (next_node and next_node[0] != 'human_approval'):
        return "error", {"message": "Attempting invalid action"}

    await graph.aupdate_state(config=thread, values={"approved": action}, as_node="human_approval")

    async def event_gen():
        async for event in graph.astream_events(
            None,
            config=thread,
        ):
            event_type = event["event"]
            node_name = event.get("metadata", {}).get("langgraph_node")

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

    return "success", event_gen