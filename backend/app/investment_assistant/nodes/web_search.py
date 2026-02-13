from investment_assistant.states import InterviewState
from investment_assistant.utils.web_search import search_engine
from investment_assistant.utils.data_processing import format_web_search_documents

async def search_web(state: InterviewState) -> InterviewState:
    """ Retrieve docs from web search """

    if state.error:
        return {}

    search_query = state.search_query

    if not search_query.strip():
        return {
            "context": ["<Document>Web search skipped: empty query</Document>"]
        }
    
    try:
        # Search web
        data = await search_engine.ainvoke({"query": search_query})
        search_docs = data.get("results", data)
        
        formatted_search_docs = format_web_search_documents(search_docs)

        return {"context": [formatted_search_docs]}

    except Exception as e:
        return {
            "error": True,
            "error_message": 'Web search failed.'
        }
