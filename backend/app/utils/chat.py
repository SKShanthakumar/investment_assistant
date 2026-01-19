from langgraph.graph.state import CompiledStateGraph

async def validate_thread(graph: CompiledStateGraph, thread: dict):
    """Validate whether the thread exists and is waiting for human approval."""

    # Check thread already exists
    state = await graph.aget_state(
        config=thread
    )
    if not state[-3]:
        return False

    # Check whether this thread waits for human approval
    history = [state async for state in graph.aget_state_history(config=thread)]
    next_node = history[0].next

    return next_node and next_node[0] == 'human_approval'