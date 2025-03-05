import torch
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification
from sklearn.preprocessing import LabelEncoder
from preprocess import get_tokens  # Assuming this is the same preprocessing module

class TextDataset(Dataset):
    def __init__(self, texts, tokenizer, max_length=128):
        # Ensure texts are strings
        texts = [str(text) for text in texts]
        
        # Tokenize inputs
        self.encodings = tokenizer(
            texts, 
            truncation=True, 
            padding=True, 
            max_length=max_length, 
            return_tensors='pt'
        )
    
    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        return item
    
    def __len__(self):
        return len(self.encodings['input_ids'])

def load_model(model_path, num_labels):
    # Initialize model with the same configuration as during training
    model = BertForSequenceClassification.from_pretrained(
        'bert-base-uncased', 
        num_labels=num_labels
    )
    
    # Load the saved state dictionary
    model.load_state_dict(torch.load(model_path))
    
    # Move to GPU if available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    
    # Set to evaluation mode
    model.eval()
    
    return model, device

def classify_new_data(model_path, new_data):
    # Preprocess new data (apply tokenization)
    new_data = [str(text) for text in new_data]
    new_tokens = [get_tokens(text) for text in new_data]
    
    # Load tokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    
    # Recreate label encoder (you might want to save/load this separately in a real scenario)
    label_encoder = LabelEncoder()
    label_encoder.fit(['Non-biased'])  # Add all original labels here
    num_labels = len(label_encoder.classes_)
    
    # Create dataset
    new_dataset = TextDataset(new_tokens, tokenizer)
    new_loader = DataLoader(new_dataset, batch_size=8, shuffle=False)
    
    # Load model
    model, device = load_model(model_path, num_labels)
    
    # Perform classification
    all_predictions = []
    
    with torch.no_grad():
        for batch in new_loader:
            # Move batch to device
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            
            # Get model outputs
            outputs = model(input_ids, attention_mask=attention_mask)
            
            # Get predictions
            preds = torch.argmax(outputs.logits, dim=1)
            
            # Convert to numpy and extend results
            all_predictions.extend(preds.cpu().numpy())
    
    # Decode predictions back to original labels
    decoded_predictions = label_encoder.inverse_transform(all_predictions)
    
    return decoded_predictions

# Example usage
if __name__ == '__main__':
    # Path to your saved model (modify this to match your saved model's filename)
    model_path = 'models/model_0.xxxx.pt'
    
    # New data to classify
    new_texts = [
        "Your first text to classify",
        "Another text to classify",
        "Yet another example text"
    ]
    
    # Perform classification
    results = classify_new_data(model_path, new_texts)
    
    # Print results
    for text, prediction in zip(new_texts, results):
        print(f"Text: {text}")
        print(f"Predicted Label: {prediction}")
        print("---")