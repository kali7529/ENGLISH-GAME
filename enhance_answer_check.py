# Script to enhance the checkAnswer function with trim for better comparison
import re

# Read the file
with open(r"c:\Users\AAHIL\Videos\ENGLISH GAME\templates\game.html", 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the comparison line
old_line = 'if (user.toLowerCase() === correct.toLowerCase()) {'
new_line = 'if (user.trim().toLowerCase() === correct.trim().toLowerCase()) {'

# Do the replacement
content = content.replace(old_line, new_line)

# Write back
with open(r"c:\Users\AAHIL\Videos\ENGLISH GAME\templates\game.html", 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Enhanced checkAnswer function - now handles both case AND extra whitespace!")
print("   Sentence Slayer will accept answers in ANY case (upper, lower, mixed)")
