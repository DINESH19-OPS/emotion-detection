import pandas as pd
import string
import pickle
import nltk
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Download stopwords (only first time)
nltk.download('stopwords')

# Load the train.txt dataset
data = pd.read_csv("train.txt", sep=';', names=["text", "emotion"])

# Text cleaning function
def clean_text(text):
    text = text.lower()
    text = ''.join([char for char in text if char not in string.punctuation])
    return text

# Apply cleaning
data['text'] = data['text'].apply(clean_text)

X = data['text']
y = data['emotion']

# Split data into train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create ML pipeline
model = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english')),
    ('classifier', LogisticRegression(max_iter=300))
])

# Train model
model.fit(X_train, y_train)

# Calculate accuracy
accuracy = model.score(X_test, y_test)
print("Model Accuracy:", accuracy)

# Save trained model
pickle.dump(model, open("emotion_model.pkl", "wb"))

print("Model saved successfully!")