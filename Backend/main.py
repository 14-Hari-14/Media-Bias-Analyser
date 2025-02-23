from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)


class TextData(BaseModel):
    text: str


@app.post("/analyze")
async def analyze_text(data: TextData):
    text = data.text
    print("Received text:", text)
    
    return {
        "status": "success",
        "message": "Text received successfully.",
        "bias_report": "neutral"  
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)