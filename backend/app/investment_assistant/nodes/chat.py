from langchain.messages import SystemMessage
from langfuse import observe

from investment_assistant.states import ResearchStateWithMessage
from investment_assistant.utils.models import llm_call
from investment_assistant.prompts.chat import system_prompt


@observe
async def general_chat(state: ResearchStateWithMessage):
    """General chat state update"""

    response = await llm_call([SystemMessage(content=system_prompt), *state.messages])

    return {"messages": response}