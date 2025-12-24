from langchain_community.document_loaders import WikipediaLoader

from investment_assistant.states import InterviewState

def search_wikipedia(state: InterviewState) -> InterviewState:
    """ Retrieve docs from wikipedia """

    # Search query
    search_query = state.search_query
    
    # Search
    search_docs = WikipediaLoader(query=search_query, load_max_docs=2).load()

     # Format
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}
