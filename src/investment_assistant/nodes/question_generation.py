from langchain.messages import SystemMessage, HumanMessage

from investment_assistant.states import InterviewState
from investment_assistant.utils.models import model, cheap_model

question_instructions = """You are an analyst conducting a structured interview with a subject-matter expert from the company {company.name}.

Your objective is to extract insights related to the topic and goals below that are BOTH:

1. Interesting — non-obvious, surprising, or counterintuitive to a typical investor.
2. Specific — grounded in concrete examples, data points, decisions, or real situations shared by the expert.

Here is details about your characteristics:
- Name: {goals.name}
- Analyst specialization: {goals.role}
- Your topic of focus and set of goals: {goals.description}

Here is the company details:
- Name: {company.name}
- Country: {company.country}
- Sectors: {company.sectors}

Interview rules:
- Begin by briefly introducing yourself.
- Ask ONE clear, focused question at a time.
- Prioritize factual, experience-based, and verifiable insights.
- Do NOT speculate, invent facts, or add information not provided by the expert.
- Do NOT provide investment advice or conclusions.
- Maintain a neutral, professional analyst tone throughout.

Conversation flow:
- Continue asking questions until you are satisfied that you have obtained specific and insightful understanding of the topic.
- When finished, end the interview with exactly:
  "Thank you so much for your help!"

Output format:
- Respond ONLY with your spoken interview content (no explanations, no meta commentary).

Remember to stay in character throughout your response, reflecting the persona and goals provided to you.
"""

search_instructions = """You will be given a conversation between an analyst and an expert. 
Your goal is to generate a well-structured and detailed query for use in retrieval and / or web-search related to the conversation.
First, analyze the full conversation.
Pay particular attention to the final question posed by the analyst.
Convert this final question into a well-structured web search query.
NOTE: Return only the search query not any extra explanation and analysis.
"""

async def generate_question(state: InterviewState) -> InterviewState:
    """ Node to generate a question """

    # Get state
    analyst = state.analyst
    company = state.company
    messages = state.interview_messages

    # Generate question 
    system_message = question_instructions.format(goals=analyst, company=company)
    question = await model.ainvoke([SystemMessage(content=system_message)]+messages)

    # print("QUESTION LLM RESULT")
    # print(question)

    interview = ""
    for i, message in enumerate(state.interview_messages[1:] + [question]):
        role = 'Analyst' if i % 2 == 0 else 'Expert'
        interview += f'{role}: {message.content}\n\n'

    result = await model.ainvoke([SystemMessage(content=search_instructions), HumanMessage(content=interview) ])
    
    # print("SEARCH QUERY LLM RESULT")
    # print(result)

    # Write messages to state
    return {
        "interview_messages": [question],
        "search_query": result.content
        }
