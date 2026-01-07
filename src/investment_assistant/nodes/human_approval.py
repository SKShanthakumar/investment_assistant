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
    pass

async def should_continue(state: ResearchStateWithMessage):
    """ Return the next node to execute """

    if state.approved:
        analysts = [Analyst(name=analyst["name"], role=analyst["role"], description=analyst["description"]) for analyst in analyst_data]
        company = Company(name=state.company_name, country=state.country, sectors=state.sectors)
        return [Send("conduct_interview", {
            "analyst": analyst,
            "company": company,
            "interview_messages": [HumanMessage(content=f"So you said you are conducting an interview with an expert from {company.name}, {company.country} focusing on {" ".join(analyst.role.split()[:-1] + ["Analysis"])}?")]
        }) for analyst in analysts]
    
    return "gather_company_info"
