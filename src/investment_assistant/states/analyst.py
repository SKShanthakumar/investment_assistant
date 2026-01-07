from pydantic import BaseModel, Field
from typing import Annotated, List
from langgraph.graph.message import add_messages
import operator
from langchain.messages import AnyMessage


class Analyst(BaseModel):
    name: str = Field(description="Name of the analyst.")
    role: str = Field(description="Role of the analyst in the context of the topic.")
    description: str = Field(description="Description of the analyst focus, concerns, and motives.")
    
    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nDescription: {self.description}\n"

class Company(BaseModel):
    name: str
    country: str
    sectors: List[str]

class InterviewState(BaseModel):
    max_num_turns: int = 2
    context: Annotated[List[str], operator.add] = []# Source docs
    analyst: Analyst # Analyst asking questions
    company: Company # Company for which research is being conducted
    interview: str = "" # Interview transcript
    sections: List[str] = [] # Final key we duplicate in outer state for Send() API
    interview_messages: Annotated[List[AnyMessage], add_messages]
    search_query: str = ""
