from langchain.messages import SystemMessage, HumanMessage
from langfuse import observe

from investment_assistant.states import InterviewState
from investment_assistant.utils.models import llm_call
from investment_assistant.prompts.question_generation import ask_question_prompt, search_query_prompt


async def generate_search_query(messages):
    interview = ""
    for i, message in enumerate(messages):
        role = 'Analyst' if i % 2 == 0 else 'Expert'
        interview += f'{role}: {message.content}\n\n'

    result = await llm_call([SystemMessage(content=search_query_prompt), HumanMessage(content=interview)])

    return result.content

@observe
async def generate_question(state: InterviewState) -> InterviewState:
    """ Node to generate a question by analyst agent and derive search query from it """
    
    if state.error:
        return {}

    analyst = state.analyst
    company = state.company
    messages = state.interview_messages

    try:
        # Generate question 
        system_message = ask_question_prompt.format(goals=analyst, company=company)
        question = await llm_call([SystemMessage(content=system_message)]+messages)

        # Generate search query for web search
        search_query = await generate_search_query([*state.interview_messages[1:], question])

        return {
            "interview_messages": [question],
            "search_query": search_query
            }

    except Exception as e:
        return {
            "error": True,
            "error_message": 'Question generation failed.'
        }