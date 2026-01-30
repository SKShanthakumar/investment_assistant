from pydantic import BaseModel, Field
from typing import Literal
from langchain.messages import SystemMessage, HumanMessage
from langfuse import observe

from investment_assistant.utils.models import llm_call_with_structured_output
from investment_assistant.prompts.intent_classification import system_prompt
from investment_assistant.states import ResearchStateWithMessage

class IntentClassification(BaseModel):
    intent: Literal["company_research", "general_chat"] = Field(
        description=(
            "The classified intent of the user input. "
            "'company_research' is used when the user asks to research, analyze, or evaluate a specific company or its stock. "
            "'general_chat' is used for general financial questions, concept explanations, or high-level investing discussions that do not involve researching a specific company."
        )
    )


@observe
async def classify_intent(state: ResearchStateWithMessage):
    """
    Classify the intent of the user input as either 'company_research' or 'general_chat'.
    """
    user_query = state.messages[-1].content
    
    result = await llm_call_with_structured_output([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Classify the following user input: '{user_query}'")
    ], IntentClassification)

    if result.intent == "company_research":
        return "gather_company_info"
    return "general_chat"
