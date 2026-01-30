from langchain.messages import HumanMessage
from langgraph.types import Send

from investment_assistant.states import ResearchStateWithMessage
from investment_assistant.states import Analyst, Company
from investment_assistant.utils.analysts import analyst_data
from investment_assistant.prompts.human_approval import interview_initiate_prompt


def human_in_the_loop(state: ResearchStateWithMessage):
    pass

def build_interview_send(analyst: Analyst, company: Company) -> Send:
        """
        Create a Send event for initiating an interview with a given analyst.
        """

        # Analyst role is like - 'Fundamental Analyst'. Changing that to 'Fundamental Analysis' format
        interview_focus = " ".join(
            analyst.role.split()[:-1] + ["Analysis"]
        )

        initiate_prompt = interview_initiate_prompt.format(
            company_name=company.name,
            country=company.country,
            focus=interview_focus,
        )

        return Send(
            "conduct_interview",
            {
                "analyst": analyst,
                "company": company,
                "interview_messages": [
                    HumanMessage(content=initiate_prompt)
                ],
            },
        )

async def should_continue(state: ResearchStateWithMessage):
    """
    Decision making node:
    - If approved -> fan out interviews
    - Else -> go back to gather_company_info
    """

    if state.approved:
        analysts = [
            Analyst(
                name=analyst["name"],
                role=analyst["role"],
                description=analyst["description"]
                )
            for analyst in analyst_data
            ]
        
        company = Company(
            name=state.company_name,
            country=state.country,
            sectors=state.sectors
            )
        
        return [build_interview_send(analyst, company) for analyst in analysts]
    
    return "gather_company_info"
