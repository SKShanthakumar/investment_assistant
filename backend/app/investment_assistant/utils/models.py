from langchain_groq import ChatGroq
from langchain.messages import AnyMessage
from typing import List
from dotenv import load_dotenv

load_dotenv()

MAIN_MODEL = "llama-3.3-70b-versatile"
MAIN_FALLBACK_MODEL = "openai/gpt-oss-120b"

LITE_MODEL = "llama-3.1-8b-instant"
LITE_FALLBACK_MODEL = "openai/gpt-oss-20b"


async def llm_call(messages: List[AnyMessage], lite: bool = False):
    """
    A singleton model call function that calls llm
    Toggles different model in case of token limit error
    """
    model_name = MAIN_MODEL if not lite else LITE_MODEL
    model = ChatGroq(model_name=model_name, streaming=True)

    try:
        return await model.ainvoke(messages)
    
    except:
        model_name = MAIN_FALLBACK_MODEL if not lite else LITE_FALLBACK_MODEL
        model = ChatGroq(model_name=model_name, streaming=True)
        
        return await model.ainvoke(messages)


async def llm_call_with_structured_output(messages: List[AnyMessage], schema):
    """
    A singleton model call function that calls llm with structured output
    Toggles different model in case of token limit error
    """
    model = ChatGroq(model_name=MAIN_MODEL, streaming=True).with_structured_output(schema)

    try:
        return await model.ainvoke(messages)
    
    except:
        model = ChatGroq(model_name=MAIN_FALLBACK_MODEL, streaming=True).with_structured_output(schema)
        
        return await model.ainvoke(messages)
