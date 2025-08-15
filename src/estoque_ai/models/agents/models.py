import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

key_gemini = os.getenv("GOOGLE_API_KEY")
key_grok = os.getenv("GROQ_API_KEY")

llm_gemini = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=key_gemini,
    temperature=1,

)


llm_groq = ChatGroq(
    api_key=key_grok,
    model_name="llama3-70b-8192",
    temperature=0.7
)
