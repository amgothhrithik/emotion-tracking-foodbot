import torch
from transformers import RobertaForSequenceClassification,RobertaTokenizer

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

path = r"D:\env\chatbot_food_env\checkpt_2"
model=RobertaForSequenceClassification.from_pretrained(path, local_files_only=True).to(device)
tokenizer= RobertaTokenizer.from_pretrained("roberta-base")
emotion_label=['admiration', 'amusement', 'anger', 'annoyance', 'approval', 'caring',
               'confusion', 'curiosity', 'desire', 'disappointment', 'disapproval', 'disgust',
               'embarrassment', 'excitement', 'fear', 'gratitude', 'grief', 'joy', 'love',
               'nervousness', 'optimism', 'pride', 'realization', 'relief', 'remorse', 'sadness',
               'surprise', 'neutral']

def predict_emotion(text,  threshold=0.15):

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding="max_length", max_length=128).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    probs = torch.sigmoid(logits)  # Convert logits to probabilities
    predicted_labels = (probs > threshold).int().tolist()[0]  # Apply threshold

    # Get emotion names

    predicted_emotions = [emotion_label[i] for i, val in enumerate(predicted_labels) if val == 1]

    return predicted_emotions

