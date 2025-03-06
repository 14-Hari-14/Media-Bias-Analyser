import pandas as pd
import torch
import os
import json
from torch.utils.data import DataLoader
from transformers import BertTokenizer, BertForSequenceClassification
from torch.optim import AdamW
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import f1_score

from preprocess import TextDataset, get_tokens


def get_data():
    data = pd.read_csv('raw_labels_SG1.csv', sep=';')[:70]
    
    try:
        data['tokens'] = data['text'].apply(get_tokens)
    except Exception as e:
        print(f"Error in tokenization: {e}")
        return None
    
    data.loc[data['label_bias'] == 'Non-biased', 'type'] = 'Non-biased'
    
    columns = ['tokens', 'type']
    data = data[columns]
    
    print("Data loaded")
    print(data.head())
    return data

def train_model():    
    data = get_data()
    
    X = data['tokens'].tolist()
    y = data['type'].tolist()
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    label_encoder = LabelEncoder()
    y_train_encoded = label_encoder.fit_transform(y_train)
    y_test_encoded = label_encoder.transform(y_test)
    
    # Store the label mapping for later use during inference
    label_mapping = {i: label for i, label in enumerate(label_encoder.classes_)}
    
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    num_labels = len(label_encoder.classes_)
    
    train_dataset = TextDataset(X_train, y_train_encoded, tokenizer)
    test_dataset = TextDataset(X_test, y_test_encoded, tokenizer)
    
    train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=8, shuffle=False)
    
    model = BertForSequenceClassification.from_pretrained(
        'bert-base-uncased', 
        num_labels=num_labels
    )
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    
    # Optimizer
    optimizer = AdamW(model.parameters(), lr=2e-3)
    
    # Training loop
    model.train()
    for epoch in range(3):
        for batch in train_loader:
            optimizer.zero_grad()
            
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            outputs = model(
                input_ids, 
                attention_mask=attention_mask, 
                labels=labels
            )
            
            loss = outputs.loss
            loss.backward()
            optimizer.step()
    
    # Evaluation
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            outputs = model(
                input_ids, 
                attention_mask=attention_mask
            )
            
            preds = torch.argmax(outputs.logits, dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    # Calculate F1 score
    f1 = f1_score(all_labels, all_preds, average='weighted')
    print(f"F1 score: {f1}")
    
    # Save additional model metadata in a config file
    config = {
        'num_labels': num_labels,
        'label_mapping': label_mapping,
        'f1_score': float(f1)
    }
    
    return model, config

def save_model(model, config):
    if model is not None:
        # Save with a fixed name instead of using F1 score in the filename
        model_path = f'models/model_{float(config["f1_score"]):.4f}.pt'
        config_path = f'models/model_config_{float(config["f1_score"]):.4f}.json'
        
        # Save the model
        torch.save(model.state_dict(), model_path)
        
        # Save the config with label mapping
        with open(config_path, 'w') as f:
            json.dump(config, f)
            
        print(f"Model saved to {model_path}")
        print(f"Model config saved to {config_path}")
    else:
        print("No model to save")

if __name__ == '__main__':
    model, config = train_model()
    save_model(model, config)