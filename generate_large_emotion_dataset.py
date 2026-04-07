import random

emotions = {
    "joy": [
        "I feel very happy today",
        "This makes me smile",
        "I am feeling wonderful",
        "Life feels beautiful today",
        "I feel cheerful",
        "Everything is going great",
        "I am really enjoying this moment",
        "Today is a fantastic day"
    ],

    "sadness": [
        "I feel very sad today",
        "My heart feels heavy",
        "I feel lonely",
        "Nothing feels good today",
        "I feel down and depressed",
        "Today is a gloomy day",
        "I miss the past",
        "I feel emotionally drained"
    ],

    "anger": [
        "I am extremely angry",
        "This situation makes me furious",
        "I cannot tolerate this anymore",
        "I feel rage building inside me",
        "This makes me very mad",
        "I am frustrated with everything",
        "I feel irritated",
        "This is unacceptable"
    ],

    "fear": [
        "I feel scared right now",
        "I am afraid of what might happen",
        "This situation frightens me",
        "I feel nervous and scared",
        "My heart is racing with fear",
        "I feel terrified",
        "I feel unsafe",
        "I am worried about this"
    ],

    "love": [
        "I love you so much",
        "You mean everything to me",
        "I care deeply about you",
        "My heart feels warm",
        "I feel deep affection",
        "You are very special to me",
        "I feel love and happiness",
        "I adore this moment"
    ],

    "surprise": [
        "Wow I did not expect that",
        "That shocked me",
        "This is completely unexpected",
        "I cannot believe this happened",
        "That caught me off guard",
        "This surprised me a lot",
        "I am amazed",
        "What a surprise"
    ],

    "neutral": [
        "I am just sitting here",
        "Today is a normal day",
        "Nothing special happened today",
        "I am doing my work",
        "Everything feels ordinary",
        "I am simply waiting",
        "It is a regular day",
        "I am just relaxing"
    ],

    "frustration": [
        "This is so frustrating",
        "Nothing is working properly",
        "I am tired of this problem",
        "I cannot solve this issue",
        "This situation annoys me",
        "I feel stuck",
        "I am struggling with this",
        "Everything keeps failing"
    ],

    "confusion": [
        "I do not understand this",
        "This is confusing",
        "I cannot figure this out",
        "Nothing makes sense",
        "I feel completely lost",
        "I am unsure about this",
        "This problem is complicated",
        "I feel puzzled"
    ],

    "boredom": [
        "I feel very bored",
        "This is extremely boring",
        "I have nothing to do",
        "Time is moving slowly",
        "This activity is dull",
        "I feel uninterested",
        "There is nothing exciting today",
        "I feel sleepy from boredom"
    ],

    "interest": [
        "This topic is very interesting",
        "I want to learn more",
        "This caught my attention",
        "I am curious about this",
        "I find this fascinating",
        "This is engaging",
        "I am eager to explore this",
        "This idea excites me"
    ],

    "anxiety": [
        "I feel anxious",
        "I am worried about the future",
        "My mind is full of worries",
        "I feel uneasy",
        "I cannot relax",
        "I feel stressed",
        "I am nervous about tomorrow",
        "My heart feels restless"
    ]
}

samples_per_emotion = 1000

with open("train_large.txt", "w", encoding="utf-8") as f:
    for emotion, sentences in emotions.items():
        for _ in range(samples_per_emotion):
            sentence = random.choice(sentences)
            f.write(f"{sentence};{emotion}\n")

print("Dataset created successfully with 12,000 samples!")
