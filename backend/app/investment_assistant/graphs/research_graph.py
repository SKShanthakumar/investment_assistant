from langgraph.graph import StateGraph, START, END

from investment_assistant.nodes import gather_info, human_in_the_loop, should_continue, final_report, general_chat, classify_intent
from investment_assistant.states import ResearchStateWithMessage
from investment_assistant.graphs.interview_graph import InterviewGraph

def build_research_graph(checkpointer = None):

    builder = StateGraph(ResearchStateWithMessage) 

    builder.add_node("general_chat", general_chat)
    builder.add_node("gather_company_info", gather_info)
    builder.add_node("human_approval", human_in_the_loop)
    builder.add_node("conduct_interview", InterviewGraph)
    builder.add_node("final_report", final_report)

    builder.add_conditional_edges(START, classify_intent, ['general_chat', 'gather_company_info'])
    builder.add_edge("gather_company_info", "human_approval")
    builder.add_conditional_edges("human_approval", should_continue, ["gather_company_info", "conduct_interview"])
    builder.add_edge("conduct_interview", "final_report")
    builder.add_edge("final_report", END)
    builder.add_edge("general_chat", END)

    return builder.compile(checkpointer=checkpointer, interrupt_before=["human_approval"])

ResearchGraph = build_research_graph()