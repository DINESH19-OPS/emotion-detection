from flask import Flask, request, render_template, redirect, url_for, session, flash
import torch
import re
import os
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "replace-this-in-production")

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "12345678"),
    "database": os.getenv("MYSQL_DATABASE", "emotion_app"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
}

# Load dataset
data = pd.read_csv("train.txt", sep=';', names=["text", "emotion"])
label_encoder = LabelEncoder()
label_encoder.fit(data["emotion"])

# Load trained model
model = DistilBertForSequenceClassification.from_pretrained("bert_emotion_model")
tokenizer = DistilBertTokenizerFast.from_pretrained("bert_emotion_model")

model.eval()


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def initialize_auth_tables():
    conn = None
    cursor = None
    try:
        server_conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"],
        )
        server_cursor = server_conn.cursor()
        server_cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` DEFAULT CHARACTER SET utf8mb4"
        )
        server_conn.commit()
        server_cursor.close()
        server_conn.close()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        conn.commit()
    except Error as exc:
        print(f"MySQL initialization error: {exc}")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()

def predict_emotion(text):

    text_lower = text.lower()    
    # Direct emotion detection from keywords
    if "surprise" in text_lower or "surprised" in text_lower or "wow" in text_lower or "shocking" in text_lower:
        return "surprise", 0.85, [{"emotion": "surprise", "percentage": 85}, {"emotion": "joy", "percentage": 10}, {"emotion": "excitement", "percentage": 5}]
        text_lower = re.sub(r"\b(can't|cannot)\b", "not", text_lower)
    text_lower = re.sub(r"\b(won't)\b", "not", text_lower)
    text_lower = re.sub(r"n['’]t\b", " not", text_lower)

    # Handle contrast sentences
    if "but" in text_lower:
        text_lower = text_lower.split("but")[-1]

    if len(text_lower.strip()) < 3:
        return "unknown", 0.0, []

    def build_rule_distribution(predicted_emotion, predicted_confidence):
        labels = list(label_encoder.classes_)
        if predicted_emotion not in labels:
            labels.append(predicted_emotion)

        distribution = {}
        if len(labels) == 1:
            distribution[labels[0]] = 1.0
            return distribution

        remaining_probability = max(0.0, 1.0 - predicted_confidence)
        fallback_probability = remaining_probability / (len(labels) - 1)

        for label in labels:
            if label == predicted_emotion:
                distribution[label] = predicted_confidence
            else:
                distribution[label] = fallback_probability

        return distribution

    def format_distribution(distribution):
        formatted = sorted(
            [
                {
                    "emotion": emotion_name,
                    "percentage": round(probability * 100, 2),
                }
                for emotion_name, probability in distribution.items()
            ],
            key=lambda item: item["percentage"],
            reverse=True,
        )
        # Only return top 5 emotions for clarity and accuracy
        return formatted[:5]

    keyword_emotion_rules = {
        "neutral": [
            "okay", "ok", "fine", "normal", "nothing much", "alright", "so so", "average"
        ],
        "fraustation": [
            "frustrated", "frustrating", "annoyed", "irritated", "fed up", "stuck", "can't deal"
        ],
        "confusion": [
            "confused", "confusing", "not sure", "don't understand", "unclear", "puzzled", "lost"
        ],
        "boredom": [
            "bored", "boring", "dull", "nothing to do", "monotonous", "tedious", "uninterested"
        ],
        "intrest": [
            "interested", "curious", "intrigued", "fascinated", "want to know", "engaged"
        ],
        "anxiety": [
            "anxious", "anxiety", "nervous", "worried", "worrying", "overthinking", "panic", "stressed", "uneasy",
            "terrified", "scared", "shaking", "heart is racing", "heart racing",
            "cannot focus", "can't focus", "cant focus", "not focus",
            "can't stop worrying", "cant stop worrying", "not stop worrying",
            "embarrass myself", "answer wrong", "tomorrow's exam", "tomorrow’s exam"
        ]
    }

    for emotion_name, keywords in keyword_emotion_rules.items():
        for keyword in keywords:
            if keyword in text_lower:
                distribution = build_rule_distribution(emotion_name, 0.90)
                return emotion_name, 0.90, format_distribution(distribution)

    opposite_emotion = {}

    if "not" in text_lower:
        for word in opposite_emotion:
            if word in text_lower:
                predicted_emotion = opposite_emotion[word]
                distribution = build_rule_distribution(predicted_emotion, 0.90)
                return predicted_emotion, 0.90, format_distribution(distribution)

    inputs = tokenizer(text_lower, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=1)
        predicted_class = torch.argmax(probabilities, dim=1).item()

    emotion = label_encoder.inverse_transform([predicted_class])[0]
    confidence = probabilities[0][predicted_class].item()
    distribution = {
        emotion_name: probabilities[0][index].item()
        for index, emotion_name in enumerate(label_encoder.classes_)
    }

    return emotion, confidence, format_distribution(distribution)


def render_prediction_response(text):
    emotion, confidence, emotion_distribution = predict_emotion(text)

    if confidence < 0.40:
        return render_template(
            "index.html",
            username=session.get("username"),
            emotion=None,
            confidence=None,
            emotion_distribution=[],
            input_text=text,
            warning="⚠️ Input not recognized or unclear emotion"
        )

    return render_template(
        "index.html",
        username=session.get("username"),
        emotion=emotion,
        confidence=confidence,
        emotion_distribution=emotion_distribution,
        input_text=text,
        warning=None
    )


def get_user_by_email(email):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cursor.fetchone()
    except Error:
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


def get_user_by_username(username):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        return cursor.fetchone()
    except Error:
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


def create_user(username, email, password):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, password_hash),
        )
        conn.commit()
        return True, None
    except Error as exc:
        return False, str(exc)
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("login.html")

        user = get_user_by_email(email)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("home"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not username or not email or not password:
        flash("Username, email and password are required.", "error")
        return redirect(url_for("login"))

    existing_user = get_user_by_email(email)
    if existing_user:
        flash("Email is already registered.", "error")
        return redirect(url_for("login"))

    existing_username = get_user_by_username(username)
    if existing_username:
        flash("Username is already taken.", "error")
        return redirect(url_for("login"))

    created, error_message = create_user(username, email, password)
    if not created:
        flash(f"Could not create account: {error_message}", "error")
        return redirect(url_for("login"))

    flash("Account created. Please log in.", "success")
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        text = request.form["text"]
        return render_prediction_response(text)

    return render_template(
        "index.html",
        username=session.get("username"),
        emotion=None,
        confidence=None,
        emotion_distribution=[],
        input_text="",
        warning=None,
    )


@app.route("/predict", methods=["POST"])
def predict():
    if "user_id" not in session:
        return redirect(url_for("login"))

    text = request.form["text"]
    return render_prediction_response(text)


if __name__ == "__main__":
    initialize_auth_tables()
    app.run(debug=True)