import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification
from torch.optim import AdamW # type: ignore
from sklearn.model_selection import train_test_split # type: ignore
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import f1_score

from preprocess import get_tokens

class TextDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
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
        
        # Encode labels
        self.labels = torch.tensor(labels)
    
    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item['labels'] = self.labels[idx]
        return item
    
    def __len__(self):
        return len(self.labels)

def get_data():
    try:
        data = pd.read_csv('raw_labels_SG1.csv', sep=';')[:10]
    except FileNotFoundError:
        print("Error: File 'raw_labels_SG1.csv' not found.")
        return None
    
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
    for epoch in range(3):  # 3 epochs
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
    
    return model, f1


def save_model(model, f1):
    if model is not None:
        model_filename = f'models/model_{f1:.4f}.pt'
        torch.save(model.state_dict(), model_filename)
        print(f"Model saved to {model_filename}")
    else:
        print("No model to save")

if __name__ == '__main__':
    model, f1 = train_model()
    save_model(model, f1)