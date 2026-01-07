from investment_assistant.states import InterviewState
from investment_assistant.utils.web_search import search_engine

async def search_web(state: InterviewState) -> InterviewState:
    
    """ Retrieve docs from web search """

    # Search query
    search_query = state.search_query
    
    # Search
    data = await search_engine.ainvoke({"query": search_query})
    search_docs = data.get("results", data)
    
    # Format
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}