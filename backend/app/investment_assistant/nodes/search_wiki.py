import asyncio
from langchain_community.document_loaders import WikipediaLoader

from investment_assistant.states import InterviewState
from investment_assistant.utils.data_processing import format_wikipedia_documents


async def search_wikipedia(state: InterviewState) -> InterviewState:
    """Retrieve docs from Wikipedia (async wrapper)"""

    if state.error:
        return {}

    search_query = state.search_query

    if not search_query.strip():
        return {
            "context": ["<Document>Wikipedia search skipped: empty query</Document>"]
        }

    try:
        search_docs = await asyncio.to_thread(
            lambda: WikipediaLoader(
                query=search_query,
                load_max_docs=2
            ).load()
        )

        formatted_search_docs = format_wikipedia_documents(search_docs)

        return {"context": [formatted_search_docs]}

    except Exception as e:
        return {
            "error": True,
            "error_message": 'Wikipedia search failed.'
        }
