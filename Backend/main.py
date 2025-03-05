from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

import preprocess, classify

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
    article_data = preprocess.get_article(html=text)
    tokens = preprocess.get_tokens(article_data['text'])
    predicted_class = classify.classify_text(tokens)
    article_data['predicted_class'] = predicted_class
    print(predicted_class)
    return article_data


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)