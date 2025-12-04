# Script to fix the gemini_reply function
import os

# Read the file
with open(r"c:\Users\AAHIL\Videos\ENGLISH GAME\app.py", 'r', encoding='utf-8') as f:
    lines = f.readlines()

# New function code
new_function = '''def gemini_reply(prompt):
    """Get AI response from Gemini API with grammar teacher context"""
    if not GEMINI_API_KEY: 
        return "AI Key missing. Please set GEMINI_API_KEY env var."
    
    try:
        # Add system prompt to make AI act as a grammar teacher
        grammar_teacher_context = (
            "You are Professor GrammarBot, a friendly and knowledgeable English grammar teacher. "
            "Your mission is to help students understand grammar rules, usage, and writing conventions. "
            "Always be encouraging, clear, and provide examples when explaining concepts. "
            "Keep your responses concise but informative. Use analogies when helpful. "
            "Here is the student's question:\\n\\n"
        )
        
        full_prompt = grammar_teacher_context + prompt
        
        # Standard REST call to Gemini API with increased timeout
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 800
            }
        }
        
        r = requests.post(
            GEMINI_URL, 
            params={"key": GEMINI_API_KEY}, 
            json=payload, 
            timeout=30  # Increased timeout to 30 seconds
        )
        
        if r.status_code == 200:
            response_data = r.json()
            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                return response_data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return "I received an empty response. Please try rephrasing your question."
        elif r.status_code == 429:
            return "Too many requests. Please wait a moment and try again."
        elif r.status_code == 400:
            return "Invalid request. Please try asking in a different way."
        else:
            return f"API Error: {r.status_code}. Please try again."
            
    except requests.exceptions.Timeout:
        return "Request timed out. The AI is taking too long to respond. Please try a simpler question."
    except requests.exceptions.ConnectionError:
        return "Connection error. Please check your internet connection."
    except KeyError as e:
        print(f"Gemini Response Format Error: {e}")
        return "Unexpected response format from AI. Please try again."
    except Exception as e:
        print(f"Gemini Error: {e}")
        return f"An error occurred: {str(e)}. Please try again."
'''

# Replace lines 94-104 (indices 93-103 in 0-indexed)
new_lines = lines[:93] + [new_function + '\n'] + lines[104:]

# Write back
with open(r"c:\Users\AAHIL\Videos\ENGLISH GAME\app.py", 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Function replaced successfully!")
