import torch
import json
import os
from dotenv import load_dotenv
from transformers import BertTokenizer, BertForSequenceClassification
from preprocess import get_tokens

load_dotenv()
MODELS_DIR = os.getenv('MODELS_DIR')
MODEL_PATH = os.getenv('MODEL_PATH')
CONFIG_PATH = os.getenv('CONFIG_PATH')

def load_model_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Config file not found at {CONFIG_PATH}")
        return {'num_labels': 4, 'label_mapping': {}}

def classify_text(texts):
    config = load_model_config()
    num_labels = config['num_labels']
    label_mapping = config['label_mapping']
    
    print(f"Preprocessing {len(texts)} texts...")
    tokenized_texts = [get_tokens(text) for text in texts]
    
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    
    print("Tokenizing texts...")
    encodings = tokenizer(
        tokenized_texts,
        is_split_into_words=True,  # This tells the tokenizer the input is already tokenized
        padding=True,
        truncation=True,
        max_length=128,
        return_tensors='pt'
    )
    
    # Load the model
    print(f"Loading model from {MODEL_PATH}...")
    model = BertForSequenceClassification.from_pretrained(
        'bert-base-uncased', 
        num_labels=num_labels
    )

    model.load_state_dict(torch.load(MODEL_PATH))
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    model.to(device)
    model.eval()
    
    # Process in batches
    batch_size = 8
    all_preds = []
    
    print("Making predictions...")
    with torch.no_grad():
        for i in range(0, len(tokenized_texts), batch_size):
            # Get batch
            batch_input_ids = encodings['input_ids'][i:i+batch_size].to(device)
            batch_attention_mask = encodings['attention_mask'][i:i+batch_size].to(device)
            
            outputs = model(
                batch_input_ids,
                attention_mask=batch_attention_mask
            )
            
            preds = torch.argmax(outputs.logits, dim=1)
            all_preds.extend(preds.cpu().numpy())

    print("Mapping predictions to labels...")
    # Convert keys to strings since JSON serialization turns them into strings
    label_mapping = {int(k): v for k, v in label_mapping.items()}
    all_preds = [label_mapping.get(int(pred), f"Unknown-{pred}") for pred in all_preds]
    
    print("Classification complete!")    
    return all_preds


if __name__ == '__main__':
    example_texts = [
        "This is a completely neutral statement without any bias.",
        "Women are not good at tech jobs and should stick to nurturing roles.",
        "All people deserve equal treatment regardless of their background."
    ]
    
    predictions = classify_text(example_texts)
    
    for text, pred in zip(example_texts, predictions):
        print(f"Text: {text[:50]}... | Prediction: {pred}")