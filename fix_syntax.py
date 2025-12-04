# Fix the word-wizard syntax error
with open(r"c:\Users\AAHIL\Videos\ENGLISH GAME\app.py", 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the syntax error - change variable assignment to dictionary key
old_code = '''    word_wizard_simple = [
    {
        "word": "Calm",
        "simple_word": "Relaxed",
        "definition": "Not angry or upset.",
        "example": "She stayed calm during the test."
    },
    {
        "word": "Brave",
        "simple_word": "Fearless",
        "definition": "Not scared to face danger.",
        "example": "He was brave when speaking on stage."
    },
    {
        "word": "Gentle",
        "simple_word": "Soft",
        "definition": "Kind and careful.",
        "example": "Be gentle with the puppy."
    },
    {
        "word": "Proud",
        "simple_word": "Confident",
        "definition": "Happy about something you did.",
        "example": "She felt proud of her work."
    },
    {
        "word": "Curious",
        "simple_word": "Interested",
        "definition": "Wanting to learn or know more.",
        "example": "The child was curious about space."
    },
    {
        "word": "Polite",
        "simple_word": "Respectful",
        "definition": "Speaking or acting kind to others.",
        "example": "He is polite when talking to adults."
    }
]

}'''

new_code = '''    'word-wizard': [
        {"word": "Calm", "def": "Not angry or upset", "ex": "She stayed calm during the test."},
        {"word": "Brave", "def": "Not scared to face danger", "ex": "He was brave when speaking on stage."},
        {"word": "Gentle", "def": "Kind and careful", "ex": "Be gentle with the puppy."},
        {"word": "Proud", "def": "Happy about something you did", "ex": "She felt proud of her work."},
        {"word": "Curious", "def": "Wanting to learn or know more", "ex": "The child was curious about space."},
        {"word": "Polite", "def": "Speaking or acting kind to others", "ex": "He is polite when talking to adults."},
    ]
}'''

content = content.replace(old_code, new_code)

with open(r"c:\Users\AAHIL\Videos\ENGLISH GAME\app.py", 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed word-wizard syntax error in app.py!")
