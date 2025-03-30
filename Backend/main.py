from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

import preprocess, classify
import re

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
    url: bool


@app.post("/analyze")
async def analyze_text(data: TextData):
    text = data.text
    print("Backend received: ", data.text, data.url)
    
    if data.url:
        article_data = preprocess.get_article(url=text)
    else:
        article_data = preprocess.get_article(html=text)

    article_text = article_data['text']
    sentences = [sentence for sentence in re.split(r'[.\n]', article_text) if sentence.strip()]
    classify_text, confidence = classify.classify_text(sentences)
    print(classify_text, confidence, sep="\n")
    
    left_biased_sentences = [f"{sentence} <span class='conf'>Confidence: {conf:.2f}</span>" for sentence, bias, conf in zip(sentences, classify_text, confidence) if bias == 'left']
    right_biased_sentences = [f"{sentence} <span class='conf'>Confidence: {conf:.2f}</span>" for sentence, bias, conf in zip(sentences, classify_text, confidence) if bias == 'right']
    center_biased_sentences = [f"{sentence} <span class='conf'>Confidence: {conf:.2f}</span>" for sentence, bias, conf in zip(sentences, classify_text, confidence) if bias == 'center']
    
    article_data['left'] = left_biased_sentences
    article_data['right'] = right_biased_sentences
    article_data['center'] = center_biased_sentences
    print(article_data)

    article_data.pop("movies")
    article_data.pop("text")
    
    return { 
        "status_code": 200,
        "status": "success",
        "result": article_data
        }



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)