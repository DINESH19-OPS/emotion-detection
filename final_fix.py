import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix: Replace smart quotes with regular quotes
content = content.replace('"', '"').replace('"', '"').replace("'", "'").replace("'", "'")

# Now do the keyword replacement
old = '''    keyword_emotion_rules = {
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
            "embarrass myself", "answer wrong", "tomorrow's exam", "tomorrow's exam"
        ]
    }'''

new = '''    keyword_emotion_rules = {
        "surprise": [
            "surprise", "surprised", "surprising", "wow", "oh wow", "shocking"
        ],
        "joy": [
            "happy", "joy", "joyful", "glad", "delighted", "pleased", "great", "wonderful", "fantastic"
        ],
        "fear": [
            "afraid", "fear", "scared", "terrified", "panic", "anxious", "worried", "nervous"
        ],
        "sadness": [
            "sad", "sadness", "depressed", "unhappy", "grief", "devastated", "miserable"
        ],
        "anger": [
            "angry", "anger", "furious", "mad", "rage", "hate", "irritated", "annoyed", "frustrated"
        ],
        "neutral": [
            "okay", "ok", "fine", "normal", "alright", "average", "meh"
        ],
        "excitement": [
            "excited", "exciting", "thrilled", "pumped", "hyped"
        ],
        "confusion": [
            "confused", "confusing", "not sure", "unclear", "puzzled", "lost"
        ]
    }'''

if old in content:
    content = content.replace(old, new)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Updated keyword_emotion_rules with surprise emotion")
else:
    print("ERROR: Could not find old keyword rules - smart quotes likely present")
    # Try manual search and replace
    start = content.find('keyword_emotion_rules = {')
    if start > -1:
        end = content.find('for emotion_name, keywords', start)
        if end > -1:
            # Extract and analyze the section
            section = content[start:end]
            print(f"Found section ({len(section)} chars):")
            print(section[:200])
