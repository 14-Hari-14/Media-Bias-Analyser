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


@app.post("/analyze")
async def analyze_text(data: TextData):
    text = data.text
    article_data = preprocess.get_article(html=text)
    article_text = article_data['text']
    sentences = [sentence for sentence in re.split(r'[.\n]', article_text) if sentence.strip()]
    classify_text = classify.classify_text(sentences)
    sentences_with_bias = [[sentence, bias] for sentence, bias in zip(sentences, classify_text)]
    
    left_biased_sentences = [sentence for sentence, bias in zip(sentences, classify_text) if bias == 'left']
    right_biased_sentences = [sentence for sentence, bias in zip(sentences, classify_text) if bias == 'right']
    center_biased_sentences = [sentence for sentence, bias in zip(sentences, classify_text) if bias == 'center']
    
    article_data['text'] = sentences_with_bias
    article_data['left'] = left_biased_sentences
    article_data['right'] = right_biased_sentences
    article_data['center'] = center_biased_sentences

    print(article_data)
    return article_data



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)