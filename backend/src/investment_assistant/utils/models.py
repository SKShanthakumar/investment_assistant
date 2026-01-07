from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

import os
from dotenv import load_dotenv

load_dotenv()

# model = ChatGroq(model_name='llama-3.3-70b-versatile', streaming=True)
# cheap_model = ChatGroq(model_name='llama-3.1-8b-instant', streaming=True)

# model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", google_api_key=os.getenv("GOOGLE_API_KEY"))
# model = ChatGroq(model_name='llama-3.1-8b-instant')

model = ChatGroq(model_name='openai/gpt-oss-120b', streaming=True)
cheap_model = ChatGroq(model_name='openai/gpt-oss-20b', streaming=True)