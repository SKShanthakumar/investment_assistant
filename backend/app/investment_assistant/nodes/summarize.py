from langchain.messages import HumanMessage, SystemMessage, AIMessage, RemoveMessage
from typing import List
from langfuse import observe

from investment_assistant.states import ResearchStateWithMessage
from investment_assistant.utils.models import llm_call
from investment_assistant.prompts.summarize import system_prompt


TOKEN_LIMIT = 4000

def get_conversation_string(messages: List[HumanMessage | AIMessage]):
    conversation = []

    for message in messages:
        role = 'AI: ' if isinstance(message, AIMessage) else "USER: "
        conversation.append(role + message.content)

    return '\n\n'.join(conversation)


@observe
async def summarize_conversation(chat: List[HumanMessage | AIMessage], summary: str):
    if summary:
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\nExtend the summary by taking into account the new conversation above:"
        )
        
    else:
        summary_message = "Create a summary of the conversation above:"

    prompt = get_conversation_string(chat) + '\n\n' + summary_message
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
        ]
    
    response = await llm_call(messages, lite=True)
    
    return response.content


def calculate_tokens(messages: List[HumanMessage | AIMessage]):
    conversation_string = ''.join([message.content for message in messages])
    
    # ideal token length is 4 characters
    return len(conversation_string) // 4


async def token_limit_checker(state: ResearchStateWithMessage):
    """ Checks token count and initiates chat summarization if threshold limit is reached """
    
    if state.error:
        return {}

    messages = state.messages
    summary = state.summary
    delete_messages = []    # List messages to truncate - remains empty if summarization is not triggered

    token_count = calculate_tokens(messages)

    try:
        if token_count > TOKEN_LIMIT:
            summary = await summarize_conversation(messages, summary)

            # Retaining last 2 messages
            delete_messages = [RemoveMessage(id=m.id) for m in messages[:-2]]
        
        return {"summary": summary, "messages": delete_messages}

    except Exception as e:
        return {
            "error": True,
            "error_message": 'Summarization failed.'
        }
