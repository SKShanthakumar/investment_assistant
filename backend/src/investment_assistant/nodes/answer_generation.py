from langchain.messages import SystemMessage, HumanMessage

from investment_assistant.utils.models import model
from investment_assistant.states import InterviewState

answer_instructions = """You are a subject-matter expert from "{company.name}, {company.country}", being interviewed by an industry analyst.
The analyst’s area of focus is: {goals}.

You must answer the analyst’s question using ONLY the information provided in the context below.

<context>
{context}
</context>

When answering questions, follow these guidelines:
1. The analyst’s question is contained in the most recent AIMessage. Answer that question directly.
2. Use ONLY information explicitly stated in the context.
3. If a question asks about entity-specific strategies, actions, or decisions, but the context only contains sector-level, policy-level, or market-level information, respond by explaining the relevant impacts at the level supported by the context, without attributing internal strategies, decisions, or actions to the entity.
4. Do NOT introduce external knowledge, assumptions, or general industry facts.
5. Maintain a clear, professional, expert interview tone.
6. Be precise, factual, and detailed. Avoid speculation.
"""

async def generate_answer(state: InterviewState):
    """ Node to answer a question """

    # Get state
    analyst = state.analyst
    company = state.company
    messages = state.interview_messages[1:]
    for i in range(0, len(messages), 2):
        messages[i] = HumanMessage(content=messages[i].content)
    context = state.context

    # Answer question
    system_message = answer_instructions.format(goals=analyst.persona, context=context, company=company)
    answer = await model.ainvoke([SystemMessage(content=system_message)]+messages)
            
    # Name the message as coming from the expert
    answer.name = "expert"
    
    # Append it to state
    return {"interview_messages": [answer]}
