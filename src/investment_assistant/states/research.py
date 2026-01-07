from pydantic import BaseModel, Field
from typing import Annotated, List
from langgraph.graph.message import add_messages
from langchain.messages import AnyMessage
import operator


class ResearchState(BaseModel):
    company_name: str | None = Field(None, description="Name of the company for which research is being undertaken")
    stock_symbol: str | None = Field(None, description="Stock symbol of the company if it is publicly traded")
    is_public: bool = Field(False, description="Whether the company is public or private")
    country: str | None = Field(None, description="Country where the company is headquartered")
    sectors: list[str] | None = Field(default_factory=list, description="Sectors in which the company operates")

class ResearchStateWithMessage(ResearchState):
    messages: Annotated[List[AnyMessage], add_messages]
    sections: Annotated[List[str], operator.add]
    approved: bool = False
    