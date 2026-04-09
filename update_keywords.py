import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the keyword_emotion_rules dictionary
pattern = r'keyword_emotion_rules = \{.*?\n    \}'
replacement = '''keyword_emotion_rules = {
        "surprise": [
            "surprise", "surprised", "surprising", "wow", "oh wow", "shocking",
            "astonished", "astounded", "stunned", "unbelievable"
        ],
        "joy": [
            "happy", "joy", "joyful", "glad", "delighted", "pleased", "great", "wonderful",
            "fantastic", "excellent", "awesome", "beautiful"
        ],
        "fear": [
            "afraid", "fear", "scared", "terrified", "panic", "anxious", "worried",
            "nervous", "frightened", "petrified", "dread"
        ],
        "sadness": [
            "sad", "sadness", "depressed", "unhappy", "grief", "devastated",
            "miserable", "sorrowful", "down", "gloomy"
        ],
        "anger": [
            "angry", "anger", "furious", "mad", "rage", "hate", "irritated",
            "annoyed", "frustrated", "livid", "enraged"
        ],
        "neutral": [
            "okay", "ok", "fine", "normal", "alright", "average", "meh"
        ],
        "excitement": [
            "excited", "exciting", "thrilled", "pumped", "hyped"
        ],
        "confusion": [
            "confused", "confusing", "not sure", "unclear", "puzzled", "lost"
        ],
        "disgust": [
            "disgusted", "disgusting", "gross", "yuck", "ew", "revolting", "awful"
        ]
    }'''

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated keyword_emotion_rules successfully")
