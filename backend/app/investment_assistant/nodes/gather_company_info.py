from langchain.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field
from langfuse import observe

from investment_assistant.states import ResearchStateWithMessage, ResearchState
from investment_assistant.utils.models import llm_call_with_structured_output
from investment_assistant.utils.web_search import search_engine
from investment_assistant.prompts.gather_company_info import company_name_extraction_prompt, structured_data_extraction_prompt
from investment_assistant.utils.chat import fake_stream

class CompanyNameOutput(BaseModel):
    company_name: str = Field(..., description="The name of the company extracted from the text.")

async def extract_company_name(messages):
    """ Extract company name from messages """

    result = await llm_call_with_structured_output([SystemMessage(content=company_name_extraction_prompt), *messages], CompanyNameOutput)
    
    return result.company_name


async def search_company_info(company_name: str):
    """ Search web for company information """

    search_result = await search_engine.ainvoke({"query": f"Is {company_name} a public company? which country does it belong to? if it is traded publicly what is the stock symbol(If in india get symbol of NSE)? In what sectors does it operate?"})
    return search_result['answer']     # Summary of web search

@observe
async def gather_info(state: ResearchStateWithMessage) -> ResearchStateWithMessage:
    """ Gathers company information from web and updates the research state. """

    messages = state.messages
    company_name = await extract_company_name(messages)
    web_search_result = await search_company_info(company_name)

    # Extract structured data from web search
    extracted_model = await llm_call_with_structured_output([SystemMessage(content=structured_data_extraction_prompt), HumanMessage(content=web_search_result)], ResearchState)

    confirmation_message = web_search_result + ' Did you mean this company?'
    
    # Custom streaming web result
    chain = RunnableLambda(func=fake_stream)
    events = [
        event async for event in chain.astream_events(confirmation_message, version="v2")
    ]

    return {"messages": AIMessage(content=confirmation_message), **extracted_model.model_dump()}
