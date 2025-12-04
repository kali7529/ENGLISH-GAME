import os, random, sqlite3, datetime, jwt, requests, json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Generate a random secret key for JWT signing
app.config['SECRET_KEY'] = os.urandom(24).hex()
CORS(app)

# ---------------- CONFIG ----------------
# Get your free API key here: https://aistudio.google.com/app/apikey
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

# ---------------- DB SETUP ----------------
def get_db():
    conn = sqlite3.connect('grammarquest.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            total_score INTEGER DEFAULT 0,
            questions_answered INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS game_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            game_type TEXT,
            score INTEGER,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            response TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
init_db()

# ---------------- AUTH HELPERS ----------------
def encode_token(uid):
    payload = {
        'user_id': uid,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def decode_token(token):
    try:
        return jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['user_id']
    except:
        return None

# ---------------- AI & GAME LOGIC ----------------
# This is the expanded question bank to prevent the game from ending too soon
TEMPLATES = {
    'tense-traveler': [
        {"q": "She ___ to the store yesterday.", "opts": ["go", "goes", "went", "going"], "ans": "went", "why": "Past tense needed for yesterday."},
        {"q": "I ___ here for 5 years.", "opts": ["live", "am living", "have lived", "lived"], "ans": "have lived", "why": "Present perfect for duration."},
        {"q": "By next year, he ___ graduated.", "opts": ["will have", "has", "had", "will"], "ans": "will have", "why": "Future perfect tense."},
        {"q": "Look! It ___ snowing.", "opts": ["is", "was", "are", "were"], "ans": "is", "why": "Present continuous for right now."},
        {"q": "If I were you, I ___ accept.", "opts": ["will", "would", "can", "shall"], "ans": "would", "why": "Second conditional (hypothetical)."},
        {"q": "They ___ dinner when the phone rang.", "opts": ["ate", "were eating", "eat", "have eaten"], "ans": "were eating", "why": "Past continuous interrupted by an event."},
        {"q": "We ___ to Japan twice.", "opts": ["go", "went", "have been", "was"], "ans": "have been", "why": "Experience requires Present Perfect."},
    ],
    'sentence-slayer': [
        {"sent": "Me and John went home.", "err": "Me and John", "corr": "John and I", "why": "'I' is the subject pronoun."},
        {"sent": "The dog lost it's bone.", "err": "it's", "corr": "its", "why": "Possessive 'its' has no apostrophe."},
        {"sent": "She don't like coffee.", "err": "don't", "corr": "doesn't", "why": "Third person singular uses doesn't."},
        {"sent": "I have saw that movie.", "err": "have saw", "corr": "seen", "why": "Present perfect uses participle 'seen'."},
        {"sent": "Between you and I.", "err": "I", "corr": "me", "why": "Prepositions are followed by object pronouns (me)."},
    ],
    'word-wizard': [
        {"word": "Calm", "def": "Not angry or upset", "ex": "She stayed calm during the test."},
        {"word": "Brave", "def": "Not scared to face danger", "ex": "He was brave when speaking on stage."},
        {"word": "Gentle", "def": "Kind and careful", "ex": "Be gentle with the puppy."},
        {"word": "Proud", "def": "Happy about something you did", "ex": "She felt proud of her work."},
        {"word": "Curious", "def": "Wanting to learn or know more", "ex": "The child was curious about space."},
        {"word": "Polite", "def": "Speaking or acting kind to others", "ex": "He is polite when talking to adults."},
    ]
}

def gemini_reply(prompt):
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
            "Here is the student's question:\n\n"
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


# ---------------- HTML VIEWS ----------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/play/<game_type>')
def play_game(game_type):
    return render_template('game.html', game_type=game_type)

@app.route('/chatpage')
def chat_page():
    return render_template('chat.html')

# ---------------- API ROUTES ----------------

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    try:
        with get_db() as conn:
            pwd = generate_password_hash(data['password'])
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, email, password) VALUES (?,?,?)", (data['username'], data['email'], pwd))
            token = encode_token(cur.lastrowid)
            return jsonify({"token": token, "uid": cur.lastrowid})
    except: return jsonify({"error": "User already exists"}), 400

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    with get_db() as conn:
        u = conn.execute("SELECT * FROM users WHERE username=?", (data['username'],)).fetchone()
        if u and check_password_hash(u['password'], data['password']):
            return jsonify({"token": encode_token(u['id']), "uid": u['id']})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    uid = decode_token(request.headers.get("Authorization"))
    if not uid: return jsonify({"error": "Unauthorized"}), 401
    with get_db() as conn:
        u = conn.execute("SELECT total_score, questions_answered FROM users WHERE id=?", (uid,)).fetchone()
        return jsonify(dict(u))

@app.route("/api/games/start", methods=["POST"])
def start_game():
    gt = request.json.get("game_type")
    pool = TEMPLATES.get(gt, TEMPLATES['tense-traveler'])
    
    # --- LOGIC FIX ---
    # Randomly select up to 10 questions from the pool.
    # If the pool has fewer than 10, it selects all of them.
    count = min(10, len(pool))
    qs = random.sample(pool, count)
    
    sid = f"{random.randint(1000,9999)}"
    return jsonify({"session_id": sid, "questions": qs})

@app.route("/api/games/complete", methods=["POST"])
def complete_game():
    uid = decode_token(request.headers.get("Authorization"))
    if not uid: return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    try:
        with get_db() as conn:
            # Update User Stats
            conn.execute("UPDATE users SET total_score = total_score + ?, questions_answered = questions_answered + ? WHERE id=?", (data['score'], data['count'], uid))
            # Log Session
            conn.execute("INSERT INTO game_sessions (user_id, game_type, score) VALUES (?,?,?)", (uid, data['game_type'], data['score']))
        return jsonify({"status": "saved"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat", methods=["POST"])
def chat():
    uid = decode_token(request.headers.get("Authorization"))
    msg = request.json.get("message")
    
    # Get response from Gemini
    resp = gemini_reply(msg)
    
    if uid:
        with get_db() as conn:
            conn.execute("INSERT INTO chat_messages (user_id, message, response) VALUES (?,?,?)", (uid, msg, resp))
    return jsonify({"response": resp})

if __name__ == "__main__":
    print("GrammarQuest-AI backend live on http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)