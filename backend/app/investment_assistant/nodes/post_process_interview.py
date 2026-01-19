from langchain.messages import SystemMessage, HumanMessage
from langchain_core.messages import get_buffer_string

from investment_assistant.states import InterviewState
from investment_assistant.utils.models import cheap_model
from investment_assistant.prompts.post_process_interview import system_prompt


def route_messages(state: InterviewState, name: str = "expert"):
    """ Route between question and answer """
    
    messages = state.interview_messages
    max_expert_responses = state.max_expert_responses

    expert_response_count = len([message for message in messages if message.name == name])

    if expert_response_count >= max_expert_responses:
        return 'write_analysis_report'

    last_question = messages[-2]
    
    if "thank you so much for your help" in last_question.content.lower():
        return 'write_analysis_report'
    return "ask_question"


async def write_analysis_report(state: InterviewState):
    """ Convert the interview transcript into a analysis report """

    messages = state.interview_messages
    interview = get_buffer_string(messages) # List of messages to single string
    analyst = state.analyst
   
    system_message = system_prompt.format(focus=analyst.description)
    section = await cheap_model.ainvoke([SystemMessage(content=system_message), HumanMessage(content=f"Here is the interview transcript: {interview}")]) 

    return {"sections": [section.content]}
