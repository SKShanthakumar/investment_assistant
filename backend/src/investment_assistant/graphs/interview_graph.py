from langgraph.graph import StateGraph, START, END

from investment_assistant.nodes import generate_answer, generate_question, search_web, search_wikipedia, save_interview, write_section, route_messages
from investment_assistant.states import InterviewState


builder = StateGraph(InterviewState)
builder.add_node("ask_question", generate_question)
builder.add_node("search_web", search_web)
builder.add_node("search_wikipedia", search_wikipedia)
builder.add_node("answer_question", generate_answer)
builder.add_node("save_interview", save_interview)
builder.add_node("write_section", write_section)

# Flow
builder.add_edge(START, "ask_question")
builder.add_edge("ask_question", "search_web")
builder.add_edge("ask_question", "search_wikipedia")
builder.add_edge("search_web", "answer_question")
builder.add_edge("search_wikipedia", "answer_question")
builder.add_conditional_edges("answer_question", route_messages,['ask_question','save_interview'])
builder.add_edge("save_interview", "write_section")
builder.add_edge("write_section", END)

InterviewGraph = builder.compile()
