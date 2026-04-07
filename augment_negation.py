import random

negation_pairs = [
    ("happy", "sadness"),
    ("joyful", "sadness"),
    ("excited", "sadness"),
    ("glad", "sadness"),
    ("thrilled", "sadness"),
    ("angry", "joy"),
    ("afraid", "joy"),
    ("scared", "joy"),
]

sentences = []

for word, label in negation_pairs:
    for _ in range(50):  # 50 variations each
        sentences.append(f"I am not {word};{label}")
        sentences.append(f"I'm not {word};{label}")
        sentences.append(f"I am really not {word};{label}")
        sentences.append(f"I am definitely not {word};{label}")

with open("train.txt", "a", encoding="utf-8") as f:
    for s in sentences:
        f.write("\n" + s)

print("Negation samples added successfully!")