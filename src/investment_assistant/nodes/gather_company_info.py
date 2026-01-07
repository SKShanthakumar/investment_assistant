from langchain.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from investment_assistant.states import ResearchStateWithMessage, ResearchState
from investment_assistant.utils.models import model, cheap_model
from investment_assistant.utils.web_search import search_engine

class CompanyNameOutput(BaseModel):
    company_name: str = Field(..., description="The name of the company extracted from the text.")

company_name_extraction = (
        "You are an information extraction system.\n"
        "Your task is to extract the single company name that the user intends to research.\n"
        "Rules:\n"
        "- Extract ONLY the company name.\n"
        "- Do NOT include stock symbols, descriptions, locations, or extra words.\n"
        "- If multiple companies are mentioned, choose the one that is the primary focus.\n"
        "- If no company is mentioned, return an empty string.\n"
        "- Do not explain your reasoning."
    )

structured_data_extraction = (
        "You are a structured data extraction system.\n"
        "Extract the research-relevant facts about the company from the conversation.\n"
        "Rules:\n"
        "- Populate fields ONLY if the information is explicitly stated or confidently implied.\n"
        "- If a field is unknown, leave it as null or an empty list.\n"
        "- Do NOT guess or infer missing information.\n"
        "- Use boolean true/false only for is_public.\n"
        "- Do not include explanations or commentary.\n"
        "- Output must strictly match the schema."
    )

data_natural_language_explain = """You will be given dictionaries in format 
        {
        "company_name": str,
        "stock_symbol": str,
        "is_public": boolean,
        "country": str,
        "sectors": List[str]
    }
    explain this company data dictionary in natural language. And ask confirmation from user.
    example 1: {
        "company_name": Tata Motors,
        "stock_symbol": TMPV,
        "is_public": True,
        "country": India,
        "sectors": ['passenger vehicles']
    }
    Tata Motors is a publicly traded company operating in India, traded with stock symbol 'TMPV'. It operates in passenger vehicles sector. Did yoy mean this company?
    
    example 2: {
        "company_name": xyz,
        "stock_symbol": None,
        "is_public": False,
        "country": India,
        "sectors": ['agentic AI']
    }
    xyz is a private company, can you provide much more clear description of the company.
    """

async def gather_info(state: ResearchStateWithMessage) -> ResearchStateWithMessage:
    """
    Gathers company information and updates the research state.

    Args:
        state (ResearchStateWithMessage): The current state of the research.
    
    Returns:
        ResearchStateWithMessage: The updated state with company information.
    """

    chat = state.messages

    messages = [SystemMessage(content=company_name_extraction)] + chat

    model_with_structure = model.with_structured_output(CompanyNameOutput)
    extracted_company = await model_with_structure.ainvoke(messages)

    company_name = extracted_company.company_name

    result = await search_engine.ainvoke({"query": f"Is {company_name} a public company? which country does it belong to? if it is traded publicly what is the stock symbol(If in india get symbol of NSE)? In what sectors does it operate?"})
    search_answer = result['answer']

    model_with_structure = model.with_structured_output(ResearchState)
    extracted_model = await model_with_structure.ainvoke([SystemMessage(content=structured_data_extraction), HumanMessage(content=search_answer)])

    result = await cheap_model.ainvoke([SystemMessage(content=data_natural_language_explain), HumanMessage(content=f"Dictionary: {extracted_model.model_dump()}")])

    return {"messages": result, **extracted_model.model_dump()}