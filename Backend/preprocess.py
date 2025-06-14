from newspaper import Article
import nltk
from nltk.tokenize import word_tokenize
import re

# Download NLTK data once
nltk.download('punkt', quiet=True)

def get_article(html=None, url=''):
    """Extracts article content from URL or HTML"""
    article = Article(url)
    
    if html:
        article.download(input_html=html)
    else:
        article.download()
        
    article.parse()
    
    return {
        'title': article.title,
        'text': article.text,
        'authors': article.authors,
        'publish_date': article.publish_date,
        'top_image': article.top_image,
        'movies': article.movies
    }

def clean_text(text):
    """Cleans raw text for LLM input"""
    print("Preprocess input length:", len(text))
    print("Preprocess input sample:", text[:200])
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove non-printable characters
    text = ''.join(char for char in text if char.isprintable())
    
    # Optional: Remove URLs (if not needed)
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    print("Preprocess output length:", len(text))
    print("Preprocess output sample:", text[:200])
    return text

def get_tokens(text):
    """Basic text tokenization (only if needed for preprocessing)"""
    return word_tokenize(text)