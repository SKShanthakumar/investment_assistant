from langchain.messages import SystemMessage, HumanMessage
from langchain_core.messages import get_buffer_string
from langfuse import observe

from investment_assistant.states import InterviewState
from investment_assistant.utils.models import llm_call
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


@observe
async def write_analysis_report(state: InterviewState):
    """ Convert the interview transcript into a analysis report """

    messages = state.interview_messages
    interview = get_buffer_string(messages) # List of messages to single string
    analyst = state.analyst
   
    system_message = system_prompt.format(focus=analyst.description)
    section = await llm_call([SystemMessage(content=system_message), HumanMessage(content=f"Here is the interview transcript: {interview}")], lite=True)

    return {"sections": [section.content]}
