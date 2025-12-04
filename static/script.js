const API = "/api";
let token = localStorage.getItem("gqToken");

// --- Sound Effects Setup ---
const hoverSound = document.getElementById("sfx-hover");
const clickSound = document.getElementById("sfx-click");

if (hoverSound) hoverSound.volume = 0.2;
if (clickSound) clickSound.volume = 0.4;

function playHover() {
    if (hoverSound) {
        hoverSound.currentTime = 0;
        hoverSound.play().catch(() => { });
    }
}

function playClick() {
    if (clickSound) {
        clickSound.currentTime = 0;
        clickSound.play().catch(() => { });
    }
}

// --- Init ---
document.addEventListener("DOMContentLoaded", () => {
    if (token) loadDashboard();
});

// --- Auth ---
async function login() {
    playClick();
    const user = document.getElementById("u_name").value;
    const pass = document.getElementById("u_pass").value;
    const msg = document.getElementById("auth-msg");

    if (!user || !pass) return msg.innerText = "Credentials required.";
    msg.innerText = "Authenticating...";

    // 1. Try Register
    let res = await fetch(`${API}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: user, email: user + "@mail.com", password: pass })
    });

    // 2. If exists, Try Login
    if (res.status !== 200) {
        res = await fetch(`${API}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: user, password: pass })
        });
    }

    const data = await res.json();
    if (data.token) {
        token = data.token;
        localStorage.setItem("gqToken", token);
        loadDashboard();
        msg.innerText = "";
    } else {
        msg.innerText = data.error || "Access Denied";
    }
}

function logout() {
    localStorage.removeItem("gqToken");
    location.reload();
}

async function loadDashboard() {
    document.getElementById("auth-section").classList.add("hidden");
    document.getElementById("dashboard").classList.remove("hidden");

    const res = await fetch(`${API}/dashboard`, {
        headers: { "Authorization": token }
    });
    const data = await res.json();

    if (data.error) return logout();

    document.getElementById("score-display").innerText = data.total_score;
    document.getElementById("qs-display").innerText = data.questions_answered;
}

// --- Navigation ---
function openGame(type) {
    if (!token) return alert("Login required.");
    playClick();
    // Delay for sound effect
    setTimeout(() => {
        window.open(`/play/${type}?token=${token}`, "_blank");
    }, 300);
}

function openChat() {
    if (!token) return alert("Login required.");
    playClick();
    setTimeout(() => {
        window.open(`/chatpage?token=${token}`, "_blank");
    }, 300);
}
