import torch
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments
)
from datasets import Dataset

# -----------------------------
# 1. Load Dataset
# -----------------------------
data = pd.read_csv("train_large.txt", sep=";", names=["text","emotion"])

# -----------------------------
# 2. Encode Labels
# -----------------------------
label_encoder = LabelEncoder()
data["label"] = label_encoder.fit_transform(data["emotion"])
num_labels = len(label_encoder.classes_)

# -----------------------------
# 3. Train / Validation Split
# -----------------------------
train_texts, val_texts, train_labels, val_labels = train_test_split(
    data["text"].tolist(),
    data["label"].tolist(),
    test_size=0.2,
    random_state=42,
    stratify=data["label"]
)

# -----------------------------
# 4. Load Tokenizer
# -----------------------------
tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

train_encodings = tokenizer(train_texts, truncation=True, padding=True)
val_encodings = tokenizer(val_texts, truncation=True, padding=True)

# -----------------------------
# 5. Convert to Dataset
# -----------------------------
train_dataset = Dataset.from_dict({
    "input_ids": train_encodings["input_ids"],
    "attention_mask": train_encodings["attention_mask"],
    "labels": train_labels
})

val_dataset = Dataset.from_dict({
    "input_ids": val_encodings["input_ids"],
    "attention_mask": val_encodings["attention_mask"],
    "labels": val_labels
})

# -----------------------------
# 6. Load Model
# -----------------------------
model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=num_labels
)

# -----------------------------
# 7. Training Arguments (Compatible Version)
# -----------------------------
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=4,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    learning_rate=2e-5,
    weight_decay=0.01,
    logging_dir="./logs"
)

# -----------------------------
# 8. Trainer
# -----------------------------
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)

# -----------------------------
# 9. Train
# -----------------------------
trainer.train()

# -----------------------------
# 10. Save Model
# -----------------------------
trainer.save_model("bert_emotion_model")
tokenizer.save_pretrained("bert_emotion_model")

print("✅ Upgraded BERT model training completed and saved!")