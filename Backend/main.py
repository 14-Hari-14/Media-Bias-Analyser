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
@limiter.limit("60/minute")  # Basic in-memory rate limiting
async def analyze_text(request: Request, data: TextData):
    print("Backend received:", data.text, "Is URL:", data.url)
    
    # Get article text
    if data.url:
        article_data = preprocess.get_article(url=data.text)
    else:
        article_data = preprocess.get_article(html=data.text)

    # Analyze with Gemini
    analysis = analyze_text_with_gemini(article_data['text'])
    
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