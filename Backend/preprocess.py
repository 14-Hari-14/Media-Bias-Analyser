from newspaper import Article
from transformers import BertTokenizer
import requests

def get_article(html=None,url=''):
    article = Article(url)
    if html:
        article.set_html(html)
        article.download(input_html=html)
    else:
        article.download()
    article.parse()
    article.nlp()
    print(article.summary)
    return {
        'title': article.title,
        'text': article.text,
        'authors': article.authors,
        'publish_date': article.publish_date,
        'top_image': article.top_image,
        'movies': article.movies,
        'summary': article.summary
    }

def get_tokens(text):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    tokens = tokenizer.tokenize(text)
    return tokens