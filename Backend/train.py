import pandas as pd
import torch
import json
import os
from dotenv import load_dotenv
from torch.utils.data import DataLoader
from transformers import BertTokenizer, BertForSequenceClassification
from torch.optim import AdamW
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import f1_score
from preprocess import TextDataset, get_tokens

load_dotenv()
DATA_PATH = os.getenv('DATA_PATH')
NUM_EPOCHS = int(os.getenv('NUM_EPOCHS'))

def get_data(source=DATA_PATH):
    data = pd.read_csv(source, sep=';')
    try:
        data['tokens'] = data['text'].apply(get_tokens)
    except Exception as e:
        print(f"Error in tokenization: {e}")
        return None
    
    data.loc[data['label_bias'] == 'Non-biased', 'type'] = 'Non-biased'
    
    columns = ['tokens', 'type']
    data = data[columns]
    data = data.dropna()
    
    print("Data loaded")
    return data

def train_model():    
    data = get_data()
    
    X = data['tokens'].tolist()
    y = data['type'].tolist()
    
    if input("Use a subset of the data for testing? (y/n): ").lower() == 'y':
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    else:
        X_train = X
        y_train = y
        test_dataset = get_data(os.getenv('TEST_DATA_PATH'))
        X_test = test_dataset['tokens'].tolist()
        y_test = test_dataset['type'].tolist()
    
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
    if input("Load model from disk? (y/n): ").lower() == 'y':
        model_path = os.getenv('MODEL_PATH')
        model_conf = os.getenv('CONFIG_PATH')
        print(f"Loading model from path {model_path}")
        model.load_state_dict(torch.load(model_path))
        with open(model_conf, 'r') as f:
            config = json.load(f)
            num_labels = config['num_labels']
            label_mapping = config['label_mapping']
    else:
        print("Training a new model")
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    
    # Optimizer
    optimizer = AdamW(model.parameters(), lr=2e-3,weight_decay=2e-3)
    
    # Training loop
    model.train()
    for epoch in range(NUM_EPOCHS):
        print(f"Epoch {epoch + 1}")
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
        print(f"Loss: {loss.item()}")
    
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
    accuracy = sum([1 for i, j in zip(all_labels, all_preds) if i == j]) / len(all_labels)
    print(f"Accuracy: {accuracy}")

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