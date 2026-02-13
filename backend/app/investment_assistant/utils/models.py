from langchain_groq import ChatGroq
from langchain.messages import AnyMessage
from typing import List
from dotenv import load_dotenv

load_dotenv()


main_llm = ChatGroq(model_name="llama-3.3-70b-versatile", streaming=True)
main_fallback_llm = ChatGroq(model_name="openai/gpt-oss-120b", streaming=True)

lite_llm = ChatGroq(model_name="llama-3.1-8b-instant", streaming=True)
lite_fallback_llm = ChatGroq(model_name="openai/gpt-oss-20b", streaming=True)


async def llm_call(messages: List[AnyMessage], lite: bool = False):
    """
    A singleton model call function that calls llm
    Toggles different model in case of token limit error
    """
    model = main_llm if not lite else lite_llm

    try:
        return await model.ainvoke(messages)
    
    except:
        model = main_fallback_llm if not lite else lite_fallback_llm
        return await model.ainvoke(messages)


async def llm_call_with_structured_output(messages: List[AnyMessage], schema):
    """
    A singleton model call function that calls llm with structured output
    Toggles different model in case of token limit error
    """
    model = main_llm.with_structured_output(schema)

    try:
        return await model.ainvoke(messages)
    
    except:
        model = main_fallback_llm.with_structured_output(schema)
        return await model.ainvoke(messages)
