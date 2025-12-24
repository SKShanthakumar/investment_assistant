from pydantic import BaseModel, Field
from langchain.messages import SystemMessage, HumanMessage
from langgraph.graph import END
from langgraph.types import Send, interrupt

from investment_assistant.states import ResearchStateWithMessage
from investment_assistant.states import Analyst, Company
from investment_assistant.utils.models import model
from investment_assistant.utils.analysts import analyst_data


class Approval(BaseModel):
    approved: bool = Field(False, description="True if user has approved, False if user requested changes")

def human_in_the_loop(state: ResearchStateWithMessage):
    approval = interrupt(
        f"{state.messages[-1].content}"
    )

    return {
        "messages": state.messages + [HumanMessage(content=approval)]
    }

def should_continue(state: ResearchStateWithMessage):
    """ Return the next node to execute """
       
    last_messages = state.messages[-2:]
    system_message = (
        "You are a decision classification system.\n"
        "Your task is to determine whether the user has approved the assistant's response.\n"
        "Rules:\n"
        "- approved = True ONLY if the user clearly confirms approval (e.g., 'yes', 'looks good', 'approved').\n"
        "- approved = False if the user requests changes, corrections, additions, or expresses uncertainty.\n"
        "- If approval is ambiguous or missing, return False.\n"
        "- Do not explain your reasoning.\n"
        "- Output must strictly match the schema."
    )
    messages = [SystemMessage(content=system_message)] + last_messages

    model_with_structure = model.with_structured_output(Approval)
    result = model_with_structure.invoke(messages)

    # for message in messages:
    #     if message is 
    #     message.pretty_print()
    if result.approved:
        analysts = [Analyst(name=analyst["name"], role=analyst["role"], description=analyst["description"]) for analyst in analyst_data]
        company = Company(name=state.company_name, country=state.country, sectors=state.sectors)
        return [Send("conduct_interview", {
            "analyst": analyst,
            "company": company,
            "interview_messages": [HumanMessage(content=f"So you said you are conducting an interview with an expert from {company.name}, {company.country} focusing on {" ".join(analyst.role.split()[:-1] + ["Analysis"])}?")]
        }) for analyst in analysts]
    
    return "gather_company_info"
