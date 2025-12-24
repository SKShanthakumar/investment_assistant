from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

import os
from dotenv import load_dotenv

load_dotenv()

# model = ChatGroq(model_name='llama-3.3-70b-versatile')
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
cheap_model = ChatGroq(model_name='llama-3.1-8b-instant')
