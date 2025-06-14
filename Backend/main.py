from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from llm_call import analyze_text_with_gemini
import preprocess
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

app = FastAPI()

# Initialize rate limiter (in-memory)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextData(BaseModel):
    text: str
    url: bool

class AnalysisResult(BaseModel):
    status_code: int
    status: str
    analysis: str
    meta: dict

@app.post("/analyze")
@limiter.limit("60/minute")
async def analyze_text(request: Request, data: TextData):
    print("Received request: URL =", data.url)
    print("Received text length:", len(data.text))
    print("Received text sample:", data.text[:200])
    
    # Get article text
    if data.url:
        article_data = preprocess.get_article(url=data.text)
        text = article_data.get('text', '')
    else:
        text = data.text  # New preprocessing for raw text
        article_data = {'title': '', 'authors': [], 'publish_date': None, 'top_image': '', 'movies': []}
    
    print("Processed text length:", len(text))
    print("Processed text sample:", text[:200])
    
    if not text or len(text.strip()) < 50:
        print("Validation failed: Empty or too short text")
        return AnalysisResult(
            status_code=400,
            status="error",
            analysis="Please provide the text you wish me to analyze. I need the text to summarize it, classify its political leaning, and explain my reasoning.",
            meta=article_data
        )
    
    # Analyze with Gemini
    analysis = analyze_text_with_gemini(text)
    print("LLM analysis:", analysis[:200])
    
    # Prepare response
    article_data.pop("movies", None)
    article_data.pop("text", None)
    
    return AnalysisResult(
        status_code=200,
        status="success",
        analysis=analysis,
        meta=article_data
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)