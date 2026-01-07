import asyncio
from langchain_community.document_loaders import WikipediaLoader
from investment_assistant.states import InterviewState


async def search_wikipedia(state: InterviewState) -> InterviewState:
    """Retrieve docs from Wikipedia (async wrapper)"""

    search_query = state.search_query
    # print("Wikipedia search query:", repr(search_query))

    if not search_query or not search_query.strip():
        return {
            "context": ["<Document>Wikipedia search skipped: empty query</Document>"]
        }

    search_docs = await asyncio.to_thread(
        lambda: WikipediaLoader(
            query=search_query,
            load_max_docs=2
        ).load()
    )

    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n'
            f'{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}
