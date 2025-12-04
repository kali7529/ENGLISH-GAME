# Fix the game.html to properly handle apostrophes in answers
import re

# Read the file
with open(r"c:\Users\AAHIL\Videos\ENGLISH GAME\templates\game.html", 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the problematic renderQuestion section for text input
old_code = '''} else if (q.sent || q.word) {
                // Text Input
                const txt = q.sent || `Definition: "${q.def}"`;
                const corr = q.corr || q.word;
                const why = q.why || q.ex;
                container.innerHTML = `
                    <h3>${txt}</h3>
                    <p style="font-size:0.8rem; color:#94a3b8">ENTER SOLUTION:</p>
                    <input type="text" id="ans-input" autocomplete="off">
                    <button onclick="checkTextAns('${corr}', '${why}')">EXECUTE</button>
                    <div id="feedback" class="feedback"></div>
                `;
            }'''

new_code = '''} else if (q.sent || q.word) {
                // Text Input
                const txt = q.sent || `Definition: "${q.def}"`;
                const corr = q.corr || q.word;
                const why = q.why || q.ex;
                // Store current question data for the button handler
                window.currentCorrect = corr;
                window.currentWhy = why;
                container.innerHTML = `
                    <h3>${txt}</h3>
                    <p style="font-size:0.8rem; color:#94a3b8">ENTER SOLUTION:</p>
                    <input type="text" id="ans-input" autocomplete="off" onkeypress="if(event.key==='Enter')submitTextAnswer()">
                    <button onclick="submitTextAnswer()">EXECUTE</button>
                    <div id="feedback" class="feedback"></div>
                `;
            }'''

content = content.replace(old_code, new_code)

# Also add the new helper function after checkTextAns
old_func = '''function checkTextAns(correct, explanation) {
            const val = document.getElementById("ans-input").value.trim();
            if (!val) return;
            checkAnswer(val, correct, explanation);
        }'''

new_func = '''function checkTextAns(correct, explanation) {
            const val = document.getElementById("ans-input").value.trim();
            if (!val) return;
            checkAnswer(val, correct, explanation);
        }

        function submitTextAnswer() {
            const val = document.getElementById("ans-input").value.trim();
            if (!val) return;
            checkAnswer(val, window.currentCorrect, window.currentWhy);
        }'''

content = content.replace(old_func, new_func)

# Write back
with open(r"c:\Users\AAHIL\Videos\ENGLISH GAME\templates\game.html", 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed Sentence Slayer input!")
print("   - Answers with apostrophes now work correctly")
print("   - Press Enter to submit answer")
