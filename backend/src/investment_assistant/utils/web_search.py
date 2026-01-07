from langchain_tavily import TavilySearch

search_engine = TavilySearch(max_results=3, include_answer=True, search_depth="advanced")
