import torch
import re
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from sklearn.preprocessing import LabelEncoder
import pandas as pd

# Load dataset to recreate label encoder
data = pd.read_csv("train.txt", sep=';', names=["text", "emotion"])
label_encoder = LabelEncoder()
label_encoder.fit(data["emotion"])

# Load trained model and tokenizer
model = DistilBertForSequenceClassification.from_pretrained("bert_emotion_model")
tokenizer = DistilBertTokenizerFast.from_pretrained("bert_emotion_model")

model.eval()


def predict_emotion(text):

    text_lower = text.lower()
    text_lower = re.sub(r"\b(can't|cannot)\b", "not", text_lower)
    text_lower = re.sub(r"\b(won't)\b", "not", text_lower)
    text_lower = re.sub(r"n['’]t\b", " not", text_lower)

    # 1️⃣ Handle contrast sentences (focus after "but")
    if "but" in text_lower:
        text_lower = text_lower.split("but")[-1]

    # 2️⃣ Detect meaningless input
    if len(text_lower) < 3:
        return "unknown", 0.0

    # Opposite emotion mapping
    opposite_emotion = {
        "happy": "sadness",
        "joy": "sadness",
        "good": "sadness",
        "excited": "sadness",
        "glad": "sadness",
        "great": "sadness",
        "amazing": "sadness",
        "okay": "sadness",

        "sad": "joy",
        "sadness": "joy",
        "depressed": "joy",
        "angry": "joy",
        "anger": "joy",
        "afraid": "joy",
        "fear": "joy",
        "upset": "joy"
    }

    # 3️⃣ Negation rule
    if "not" in text_lower:
        for word in opposite_emotion:
            if word in text_lower:
                return opposite_emotion[word], 0.90

    # 4️⃣ Tokenize input
    inputs = tokenizer(text_lower, return_tensors="pt", truncation=True, padding=True)

    # 5️⃣ Model prediction
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=1)
        predicted_class = torch.argmax(probabilities, dim=1).item()

    emotion = label_encoder.inverse_transform([predicted_class])[0]
    confidence = probabilities[0][predicted_class].item()

    return emotion, confidence


# Interactive loop
while True:
    user_input = input("Enter text (or type 'exit'): ")

    if user_input.lower() == "exit":
        break

    emotion, confidence = predict_emotion(user_input)

    # Reject unclear predictions
    if confidence < 0.60:
        print("⚠️ Input not recognized or unclear emotion")
    else:
        print(f"Predicted Emotion: {emotion}")
        print(f"Confidence: {confidence:.6f}")

    print("-" * 40)