from langchain.messages import AIMessage, SystemMessage, HumanMessage
from langchain_core.messages import get_buffer_string

from investment_assistant.states import InterviewState
from investment_assistant.utils.models import model

def save_interview(state: InterviewState):
    """ Save interviews """

    # Get messages
    messages = state.interview_messages
    
    # Convert interview to a string
    interview = get_buffer_string(messages)
    
    # Save to interviews key
    return {"interview": interview}

def route_messages(state: InterviewState, name: str = "expert"):
    """ Route between question and answer """
    
    # Get messages
    messages = state.interview_messages
    max_num_turns = state.max_num_turns

    # Check the number of expert answers 
    num_responses = len([m for m in messages if isinstance(m, AIMessage) and m.name == name])

    # End if expert has answered more than the max turns
    if num_responses >= max_num_turns:
        return 'save_interview'

    # Get the last question asked to check if it signals the end of discussion
    last_question = messages[-2]
    
    if "thank you so much for your help" in last_question.content.lower():
        return 'save_interview'
    return "ask_question"

section_writer_instructions = """You are an expert technical writer. 
Your task is to create a short, easily digestible section of a report based on an interview conducted by an analyst with a subject-matter expert from a company.
The interview conversation will be provided as input.

IMPORTANT CONTENT RULES:
- Use ONLY information explicitly present in the interview conversation.
- Do NOT add external knowledge, assumptions, or interpretations.
- If a topic is not covered in the interview, do not include it.

REPORT STRUCTURE (Markdown required):
- Use ## for the main section title
- Use ### for sub-section headers

The report must follow this exact structure:
a. ## Title  
b. ### Editorial Synthesis

TITLE GUIDELINES:
- Make the title engaging and relevant to the analyst’s focus area: {focus}

EDITORIAL SYNTHESIS GUIDELINES:
- Begin with general background or context related to the analyst’s focus area
- Highlight novel, interesting, or surprising insights from the interview
- Cover all topics discussed in the interview
- Do not mention the names of interviewers or experts

FINAL CHECK:
- Follow the required structure exactly
- Include no text before the title
"""

def write_section(state: InterviewState):
    """ Node to answer a question """

    # Get state
    interview = state.interview
    analyst = state.analyst
   
    # Write section using either the gathered source docs from interview (context) or the interview itself (interview)
    system_message = section_writer_instructions.format(focus=analyst.description)
    section = model.invoke([SystemMessage(content=system_message)]+[HumanMessage(content=f"Here is the interview transcript: {interview}")]) 
                
    # Append it to state
    return {"sections": [section.content]}
