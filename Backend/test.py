import torch, numpy as np
from fastapi.testclient import TestClient
from classify import classify_text, load_model_config, temperature_scaled_softmax
from main import app
from preprocess import get_tokens

client = TestClient(app)

def test_load_model_config():
    """Test if model config loads correctly"""
    config = load_model_config()
    assert isinstance(config, dict)
    assert 'num_labels' in config
    assert 'label_mapping' in config

def test_get_tokens():
    """Test tokenization function"""
    text = "This is a test sentence."
    tokens = get_tokens(text)
    assert isinstance(tokens, list)
    assert len(tokens) > 0
    

def test_classify_text():
    """Test text classification function"""
    texts = ["The economy is struggling due to excessive regulation.",
             "Social programs help the underprivileged survive."]
    predictions, confidences = classify_text(texts)
    
    assert len(predictions) == len(texts)
    assert len(confidences) == len(texts)
    assert all(isinstance(pred, str) for pred in predictions)
    assert all(isinstance(conf, np.float32) for conf in confidences)

def test_analyze_text():
    """Integration test for FastAPI endpoint /analyze"""
    response = client.post("/analyze", json={"text": "https://thefederalist.com/2019/02/21/facts-mass-shootings-support-gun-ownership-not-gun-control/", "url": True})
    assert response.status_code == 200
    data = response.json()
    assert "left" in data and "right" in data and "center" in data


if __name__ == "__main__":
    test_load_model_config()
    test_get_tokens()
    test_classify_text()
    test_analyze_text()
    print("All tests passed!")