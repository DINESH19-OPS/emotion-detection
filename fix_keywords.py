#!/usr/bin/env python3
"""Fix emotion detection - add surprise and other keywords"""

import re

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the keyword_emotion_rules section
start_idx = None
end_idx = None
brace_count = 0
found_start = False

for i, line in enumerate(lines):
    if 'keyword_emotion_rules = {' in line:
        start_idx = i
        found_start = True
        brace_count = 1
    elif found_start and '{' in line:
        brace_count += line.count('{')
    elif found_start and '}' in line:
        brace_count -= line.count('}')
        if brace_count == 0:
            end_idx = i
            break

if start_idx is not None and end_idx is not None:
    # Create new rules
    new_rules = '''    keyword_emotion_rules = {
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
    }
'''
    
    # Replace the section
    new_lines = lines[:start_idx] + [new_rules + '\n'] + lines[end_idx+1:]
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✓ Updated keyword_emotion_rules (lines {start_idx+1}-{end_idx+1})")
else:
    print("✗ Could not find keyword_emotion_rules section")
