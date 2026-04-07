import torch
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

# Load dataset to recreate label encoder
data = pd.read_csv("train.txt", sep=';', names=["text", "emotion"])
label_encoder = LabelEncoder()
label_encoder.fit(data["emotion"])

# Load test dataset
test_data = pd.read_csv("test.txt", sep=';', names=["text", "emotion"])
test_data["label"] = label_encoder.transform(test_data["emotion"])

# Load trained model and tokenizer
print("Loading trained model...")
model = DistilBertForSequenceClassification.from_pretrained("bert_emotion_model")
tokenizer = DistilBertTokenizerFast.from_pretrained("bert_emotion_model")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

# Tokenize and evaluate test data
print("Tokenizing and evaluating test data...")
all_predictions = []
all_labels = []

batch_size = 8
for i in range(0, len(test_data), batch_size):
    batch_texts = test_data["text"].iloc[i:i+batch_size].tolist()
    batch_labels = test_data["label"].iloc[i:i+batch_size].tolist()
    
    # Tokenize batch
    encodings = tokenizer(
        batch_texts,
        truncation=True,
        padding=True,
        return_tensors="pt"
    )
    
    input_ids = encodings["input_ids"].to(device)
    attention_mask = encodings["attention_mask"].to(device)
    
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=1)
    
    all_predictions.extend(predictions.cpu().numpy())
    all_labels.extend(batch_labels)

# Calculate metrics
accuracy = accuracy_score(all_labels, all_predictions)
precision = precision_score(all_labels, all_predictions, average='weighted', zero_division=0)
recall = recall_score(all_labels, all_predictions, average='weighted', zero_division=0)
f1 = f1_score(all_labels, all_predictions, average='weighted', zero_division=0)

print("\n" + "="*50)
print("EVALUATION RESULTS")
print("="*50)
print(f"Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-Score:  {f1:.4f}")
print("="*50)

# Confusion Matrix
cm = confusion_matrix(all_labels, all_predictions)
print("\nConfusion Matrix:")
print(cm)

# Classification Report
print("\nClassification Report:")
class_names = label_encoder.classes_
print(classification_report(all_labels, all_predictions, target_names=class_names, zero_division=0))

# Save results to file
with open("evaluation_results.txt", "w") as f:
    f.write("BERT EMOTION CLASSIFIER - EVALUATION RESULTS\n")
    f.write("="*50 + "\n")
    f.write(f"Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)\n")
    f.write(f"Precision: {precision:.4f}\n")
    f.write(f"Recall:    {recall:.4f}\n")
    f.write(f"F1-Score:  {f1:.4f}\n")
    f.write("="*50 + "\n")
    f.write("\nConfusion Matrix:\n")
    f.write(str(cm) + "\n\n")
    f.write("Classification Report:\n")
    f.write(classification_report(all_labels, all_predictions, target_names=class_names, zero_division=0))

print("\nResults saved to evaluation_results.txt")
