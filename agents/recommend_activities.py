from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
import json 
import os
from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

def recommend_activities(state):
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1,  api_key=groq_api_key)
    prompt = f"""
    Based on the following preferences and itinerary, suggest unique local activities:
    Preferences: {json.dumps(state['preferences'], indent=2)}
    Itinerary: {state['itinerary']}

    Provide suggestions in bullet points for each day if possible.
    """
    try:
        result = llm.invoke([HumanMessage(content=prompt)]).content
        return {"activity_suggestions": result.strip()}
    except Exception as e:
        return {"activity_suggestions": "", "warning": str(e)}