from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

def analyze_text_with_gemini(text: str) -> str:
    """
    Analyzes text with Gemini for political bias
    Args:
        text: Article text to analyze
    Returns:
        Analysis string with summary, leaning, and reasoning
    """
    gemini_obj = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.3
    )

    messages = [
        (
            "system",
            "You are a senior political analyst with 20+ years of experience in media bias detection. "
            "Your task is to: "
            "1. Summarize the text. The summary should be written in such a way that without even reading the original text, the reader should know the main ideas and key data points of the article. "
            "2. Classify its political leaning as Left/Center/Right."
            "3. Explain your reasoning in 2-3 sentences, highlighting key phrases or tones."
        ),
        ("human", text),
    ]

    ai_msg = gemini_obj.invoke(messages)
    print(ai_msg.content)  # Debug: Print the AI response
    return ai_msg.content