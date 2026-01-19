from langchain.messages import SystemMessage

from investment_assistant.states import ResearchStateWithMessage
from investment_assistant.utils.models import model
from investment_assistant.prompts.chat import system_prompt

async def general_chat(state: ResearchStateWithMessage):
    """General chat state update"""

    response = await model.ainvoke([SystemMessage(content=system_prompt), *state.messages])

    return {"messages": response}