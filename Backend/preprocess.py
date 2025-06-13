from newspaper import Article
import nltk
from nltk.tokenize import word_tokenize

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
        'movies': article.movies  # Can remove if not needed
    }

def get_tokens(text):
    """Basic text tokenization (only if needed for preprocessing)"""
    return word_tokenize(text)