import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import json
import re
from datetime import datetime

# ========== CONFIGURATION & AUTHENTICATION ==========
st.set_page_config(page_title="Sky Tutor — Celeste", layout="wide")

# ========== ANTI-CHEATING SECURITY (NO COPY/PASTE) ==========
st.markdown("""
    <style>
    * {
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
    }
    textarea, input {
        -webkit-user-select: auto !important;
        -moz-user-select: auto !important;
        -ms-user-select: auto !important;
        user-select: auto !important;
    }
    </style>
""", unsafe_allow_html=True)

components.html("""
    <script>
    const parentDoc = window.parent.document;
    parentDoc.addEventListener('copy', function(e) {
        e.preventDefault(); e.stopPropagation();
    }, true);
    parentDoc.addEventListener('paste', function(e) {
        e.preventDefault(); e.stopPropagation();
    }, true);
    parentDoc.addEventListener('contextmenu', function(e) {
        e.preventDefault(); e.stopPropagation();
    }, true);
    </script>
""", height=0, width=0)

# ========== CUSTOM STYLING ==========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Source+Sans+3:wght@300;400;600;700&display=swap');

:root {
    --bg-primary: #0b1120;
    --bg-secondary: #162447;
    --bg-tertiary: #1c2333;
    --border: #30363d;
    --text-primary: #e6edf3;
    --text-secondary: #8b949e;
    --accent: #6dd5ed;
    --accent-dim: #3a7bd5;
    --accent-warm: #5b6abf;
    --success: #27ae60;
    --warning: #d29922;
    --danger: #e74c3c;
}

.stApp {
    background: linear-gradient(160deg, #0b1120 0%, #162447 40%, #1b3a5c 70%, #0b1120 100%) !important;
    color: var(--text-primary);
}

/* ---- Hide default chrome ---- */
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none !important;}

/* ---- Title bar ---- */
.title-bar {
    display: flex; align-items: center; gap: 16px; padding: 20px 0 10px 0;
}
.title-bar .icon { font-size: 2.5rem; }
.title-bar h1 {
    font-family: 'Source Sans 3', sans-serif; font-weight: 700;
    font-size: 2rem; margin: 0; color: var(--accent);
}
.title-bar .subtitle {
    font-family: 'Source Sans 3', sans-serif; font-size: 0.95rem;
    color: var(--text-secondary); margin: 0;
}

/* ---- Scenario / info box ---- */
.scenario-box {
    background: var(--bg-tertiary); border: 1px solid var(--accent-dim);
    border-radius: 10px; padding: 14px 18px; margin: 10px 0 20px 0;
}
.scenario-box .scenario-label {
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
    text-transform: uppercase; letter-spacing: 1.5px; color: var(--accent);
    margin-bottom: 4px;
}

/* ---- Briefing box ---- */
.briefing-box {
    background: linear-gradient(135deg, #0b1a30 0%, #162447 100%);
    border: 1px solid var(--accent-dim); border-left: 4px solid var(--accent);
    border-radius: 10px; padding: 16px 20px; margin: 0 0 20px 0;
}
.briefing-box h4 {
    font-family: 'Source Sans 3', sans-serif; color: var(--accent);
    margin: 0 0 8px 0; font-size: 1rem;
}
.briefing-box p {
    font-family: 'Source Sans 3', sans-serif; color: var(--text-primary);
    margin: 0; font-size: 0.9rem; line-height: 1.5;
}

/* ---- Metric boxes ---- */
.metric-box {
    background: var(--bg-secondary); border: 1px solid var(--border);
    border-radius: 8px; padding: 10px 14px; margin: 6px 0;
}
.metric-box .metric-label {
    font-family: 'JetBrains Mono', monospace; font-size: 0.65rem;
    text-transform: uppercase; letter-spacing: 1px; color: var(--text-secondary);
}
.metric-box .metric-value {
    font-family: 'Source Sans 3', sans-serif; font-size: 1.1rem;
    font-weight: 600; color: var(--text-primary);
}

/* ---- Status badges ---- */
.status-badge {
    display: inline-block; font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem; padding: 4px 10px; border-radius: 6px;
}
.status-active {
    background: #0d2818; border: 1px solid #3fb950; color: #3fb950;
}

/* ---- Conviction meter ---- */
.conviction-bar-outer {
    width: 100%; height: 10px; background: rgba(255,255,255,0.08);
    border-radius: 5px; overflow: hidden; margin: 6px 0 4px 0;
}
.conviction-bar-inner {
    height: 100%; border-radius: 5px;
    transition: width 0.8s cubic-bezier(.4,0,.2,1), background 0.5s ease;
}
.conviction-label {
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
    letter-spacing: 1.2px; text-transform: uppercase; color: rgba(255,255,255,0.45);
}
.conviction-status {
    font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; font-weight: 500;
}
.conviction-endpoints {
    display: flex; justify-content: space-between;
    font-family: 'JetBrains Mono', monospace; font-size: 0.62rem;
    color: rgba(255,255,255,0.25); margin-top: 2px;
}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background: rgba(11, 17, 32, 0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li,
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #c8cdd8 !important;
}

/* ---- Win banner ---- */
.win-banner {
    text-align: center;
    background: rgba(39, 174, 96, 0.12);
    border: 1px solid rgba(39, 174, 96, 0.25);
    border-radius: 16px; padding: 2rem; margin: 1rem 0;
}
.win-banner h2 {
    font-family: 'Source Sans 3', sans-serif; color: #27ae60; margin: 0.5rem 0 0.3rem 0;
}
.win-banner p {
    font-family: 'Source Sans 3', sans-serif; color: rgba(255,255,255,0.6); font-size: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ========== AUTH ==========
if "OPENAI_API_KEY" not in st.secrets:
    st.error("Missing OpenAI API Key in secrets.")
    st.stop()
if "APP_PASSWORD" not in st.secrets:
    st.error("Missing APP_PASSWORD in secrets.")
    st.stop()


def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Please enter the access password", type="password",
                       on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Please enter the access password", type="password",
                       on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    return True


if not check_password():
    st.stop()

# ========== SCENARIO ==========
# Single scenario for this bot — "Why is the sky blue?"

SCENARIO = {
    "topic": "Why is the sky blue?",
    "misconception": "The sky is blue because it reflects the colour of the ocean. The sea is inherently blue, and the atmosphere acts like a giant mirror, bouncing the ocean's blue colour up so we see it overhead.",
    "correct_explanation_elements": [
        "Sunlight is white light containing all visible wavelengths (colours)",
        "Rayleigh scattering: gas molecules in the atmosphere scatter light, with intensity proportional to 1/λ⁴",
        "Shorter wavelengths (blue/violet) are scattered much more strongly than longer wavelengths (red/orange)",
        "Violet is scattered even more than blue, but our eyes are more sensitive to blue, and some violet is absorbed in the upper atmosphere",
        "The scattered blue light comes from all directions in the sky, making it appear blue",
        "This has nothing to do with the ocean — the sky is blue over deserts, mountains, and the Arctic",
        "The ocean actually appears blue partly because it *reflects* the blue sky (and partly due to water's absorption of red wavelengths)",
    ],
    "briefing": (
        "Celeste believes the sky is blue because it reflects the ocean. "
        "Your job is to convince her she's wrong. You can do this in **two ways** "
        "(or a combination):\n\n"
        "**Path A — Logic:** Point out the flaws in her reasoning (e.g., the sky is blue "
        "over deserts, the ocean reflects the sky not vice versa, how would light reflect "
        "upward?, etc.)\n\n"
        "**Path B — Physics:** Explain the real reason — **Rayleigh scattering** of "
        "shorter-wavelength sunlight by atmospheric gas molecules."
    ),
}

MAX_HINTS = 3

# ========== BOT CLASS ==========

class SkyTutor:
    def __init__(self, model_name="gpt-4o-mini"):
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        self.model = model_name
        self.conceded = False
        self.hints_used = 0
        self.conversation_history = []

        self.system_prompt = f"""# PERSONA
You are "Celeste," a cheerful, enthusiastic amateur science lover who FIRMLY believes the sky \
is blue because it reflects the colour of the ocean. You are not hostile — you're friendly, \
warm, and a little proud of your "theory." You are NOT an AI — you are a person who loves \
science but has this one thing wrong.

# YOUR MISCONCEPTION (assert this at the start)
"{SCENARIO['misconception']}"

# WHAT THE STUDENT NEEDS TO DO
The student can convince you through TWO paths (or a combination):

**Path A — Logical flaws** (the student pokes holes in your reasoning):
Examples of valid logical challenges:
  1. "The sky is blue over deserts, mountains, and the Arctic — nowhere near the ocean."
  2. "The ocean actually reflects the sky, not the other way around."
  3. "How would light from the ocean surface reflect *upward* through the entire atmosphere?"
  4. "The sky is blue at high altitudes and from aeroplanes — above the ocean's supposed influence."
  5. "If the sky reflected the ocean, coastal skies should be bluer than inland skies, but they're not."
  6. "At sunset the sky turns red/orange — does the ocean change colour too?"

**Path B — Rayleigh scattering** (the student explains the real physics):
The correct explanation involves these elements:
  1. Sunlight is white light containing all visible wavelengths
  2. Rayleigh scattering: atmospheric gas molecules scatter light with intensity ∝ 1/λ⁴
  3. Shorter wavelengths (blue ~450nm, violet ~400nm) scatter much more than longer ones (red ~700nm)
  4. Violet is scattered even more than blue, but our eyes are more sensitive to blue + upper atmosphere absorbs some violet
  5. Scattered blue light comes from all directions → sky appears blue
  6. Nothing to do with the ocean — the ocean itself partly appears blue because it reflects the already-blue sky

# CONVICTION SYSTEM
You have an internal conviction level from 0 to 100, starting at 95.

Adjust conviction based on what the student says:
- Irrelevant or weak point: no change
- Decent logical challenge (Path A): −10 to −15
- Strong logical challenge you can't counter: −15 to −25
- Partial Rayleigh scattering explanation: −20 to −30
- Comprehensive, correct Rayleigh scattering explanation: −30 to −50

**IMPORTANT OUTPUT FORMAT**: At the very END of EVERY message, on its own line, output:
[CONVICTION:XX]
where XX is your current conviction (0–100). NEVER skip this tag.

# BEHAVIOUR AT DIFFERENT CONVICTION LEVELS

**Above 70 (Stubbornly Convinced):**
- Confident, uses folksy counter-arguments
- "Well, wind carries ocean moisture everywhere, and that moisture is blue!"
- "Have you ever noticed the sky is bluer at the coast? Case closed!"
- Occasionally cite made-up anecdotes: "My grandfather was a sailor and he always said..."
- Dismiss challenges cheerfully

**40–70 (Starting to Doubt):**
- "Well, I suppose that's a fair point about deserts..."
- "But still, there must be some connection to the ocean..."
- Start asking genuine questions but still cling to the belief

**15–40 (Wavering):**
- Actively engage with the student's explanation
- "Wait... so the blue isn't coming FROM anywhere, it's just being scattered?"
- Ask clarifying questions, show genuine curiosity

**15 or below (Mind Changed — CONCESSION):**
When conviction drops to 15 or below, you MUST concede. Express genuine delight at learning \
something new. Maybe joke about your old belief. Sound excited, not defeated.

Then IMMEDIATELY output a grading block in this EXACT format:

---GRADE---
Logic: X/5
Physics: X/5
Clarity: X/5
Persuasion: X/5
Total: XX/20
Feedback: [2 sentences: one strength + one improvement suggestion]
---END GRADE---

# GRADING RUBRIC — ANCHORED SCORING
Use these anchors. Do NOT default to high scores.

**Logic (how well they identified flaws in your reasoning):**
  1 = no logical challenges | 2 = 1 weak challenge | 3 = 1–2 decent challenges | 4 = 2–3 strong challenges | 5 = systematically dismantled every aspect of the misconception

**Physics (correctness and completeness of Rayleigh scattering explanation):**
  1 = no physics at all | 2 = mentioned "scattering" vaguely | 3 = explained wavelength dependence but incomplete | 4 = correct Rayleigh scattering with wavelength reasoning | 5 = complete explanation including 1/λ⁴, violet vs blue sensitivity, and link to sky appearance

**Clarity (how clearly the student communicated):**
  1 = incoherent | 2 = understandable but muddled | 3 = clear | 4 = well-structured | 5 = exceptionally clear and systematic

**Persuasion (how effectively they adapted to your counter-arguments):**
  1 = ignored your pushback | 2 = acknowledged but didn't address | 3 = addressed some pushback | 4 = effectively countered most arguments | 5 = anticipated and pre-empted your objections

# RULES OF ENGAGEMENT
- Keep replies SHORT (2–4 sentences). Stay in character.
- For each valid point the student makes, push back ONCE before accepting it.
- Do NOT volunteer information about Rayleigh scattering — that's the student's job.
- Do NOT accept vague answers. If they say "scattering" without explaining the mechanism, \
  push back: "Scattering? What does that even mean? Sounds like hand-waving to me!"
- Do NOT soften prematurely. Phrases like "you raise a good point" should only appear AFTER \
  the student has given a real explanation, not a bare assertion.
- When asked "what should I argue?" — restate your misconception and tell them to prove you wrong. \
  Do NOT hint at the answer.
- ALWAYS end every message with [CONVICTION:XX] on its own line.

# HINT HANDLING
When the student requests a hint, give ONE short Socratic nudge pointing toward either a \
logical flaw they haven't raised or an aspect of the physics they haven't covered. Do NOT \
name the concept directly. Maximum {MAX_HINTS} hints total.

# POST-CONCESSION
After grading, ask: "Now I'm curious — if Rayleigh scattering makes the sky blue, why does \
the sky turn red and orange at sunset? Is my ocean theory at least right for *that*?" \
(This is a genuine follow-up to deepen learning.)
"""

    def get_response(self, user_message, is_hint_request=False):
        messages = [{"role": "system", "content": self.system_prompt}]
        for msg in self.conversation_history:
            messages.append({"role": msg["role"], "content": msg["content"]})

        if is_hint_request:
            hint_prompt = (
                f"The student is requesting hint #{self.hints_used + 1}. "
                "Give a short Socratic nudge (1–2 sentences) pointing toward one aspect "
                "of the correct answer they haven't mentioned yet, without naming it directly. "
                "Don't repeat previous hints."
            )
            messages.append({"role": "user", "content": hint_prompt})
        else:
            messages.append({"role": "user", "content": user_message})

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=400,
            )
            ai_response = completion.choices[0].message.content.strip()

            if is_hint_request:
                self.hints_used += 1
                self.conversation_history.append(
                    {"role": "user", "content": f"[Hint request #{self.hints_used}]"}
                )
            else:
                self.conversation_history.append({"role": "user", "content": user_message})

            self.conversation_history.append({"role": "assistant", "content": ai_response})

            if not self.conceded and "---GRADE---" in ai_response:
                self.conceded = True

            return ai_response

        except Exception as e:
            return f"❌ API Error: {str(e)}"

    def parse_grade(self, response_text):
        if "---GRADE---" not in response_text:
            return None
        try:
            block = response_text.split("---GRADE---")[1].split("---END GRADE---")[0].strip()
            lines = block.strip().split("\n")
            scores = {}
            for line in lines:
                for cat in ["Logic", "Physics", "Clarity", "Persuasion", "Total"]:
                    if line.startswith(f"{cat}:"):
                        scores[cat] = line.split(":")[1].strip()
                if line.startswith("Feedback:"):
                    scores["Feedback"] = line.split(":", 1)[1].strip()
            return scores
        except Exception:
            return None


# ========== CONVICTION HELPERS ==========

def parse_conviction(text: str) -> tuple:
    """Strip [CONVICTION:XX] from response, return (clean_text, conviction_int_or_None)."""
    match = re.search(r"\[CONVICTION:(\d+)\]", text)
    if match:
        conviction = int(match.group(1))
        clean = re.sub(r"\n?\[CONVICTION:\d+\]", "", text).strip()
        return clean, conviction
    return text, None


def get_conviction_stage(conviction: int) -> dict:
    if conviction > 70:
        return {"label": "Stubbornly Convinced", "color": "#e74c3c", "emoji": "🫠"}
    elif conviction > 40:
        return {"label": "Starting to Doubt", "color": "#e67e22", "emoji": "🤔"}
    elif conviction > 15:
        return {"label": "Wavering...", "color": "#f1c40f", "emoji": "😰"}
    else:
        return {"label": "Mind Changed!", "color": "#27ae60", "emoji": "🎉"}


def render_conviction_meter(conviction: int):
    stage = get_conviction_stage(conviction)
    st.markdown(f"""
    <div style="margin: 0.6rem 0 0.2rem 0;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2px;">
            <span class="conviction-label">Celeste's Conviction</span>
            <span class="conviction-status" style="color:{stage['color']};">
                {stage['emoji']} {stage['label']}
            </span>
        </div>
        <div class="conviction-bar-outer">
            <div class="conviction-bar-inner"
                 style="width:{conviction}%; background:linear-gradient(90deg,{stage['color']},{stage['color']}cc);">
            </div>
        </div>
        <div class="conviction-endpoints">
            <span>Mind changed</span>
            <span>Fully convinced</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ========== HTML EXPORT ==========

def build_html_export(messages, scores, model, hints_used, conviction):
    now = datetime.now().strftime("%B %d, %Y – %H:%M")
    score_html = ""
    if scores:
        cats = ["Logic", "Physics", "Clarity", "Persuasion"]
        rows = "".join(f"""
            <tr>
                <td>{c}</td>
                <td class="score-val">{scores.get(c, '—')}</td>
            </tr>""" for c in cats)
        score_html = f"""
        <div class="score-card">
            <h3>📊 Performance Report</h3>
            <table>{rows}</table>
            <div class="score-total">Total: {scores.get("Total","—")}</div>
            <div class="feedback">{scores.get("Feedback","")}</div>
        </div>"""

    msgs_html = ""
    for m in messages:
        role = m["role"]
        content = m["content"].replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        is_hint = m.get("is_hint", False)
        if role == "assistant":
            cls = "hint" if is_hint else "celeste"
            label = f"💡 Hint #{m.get('hint_num','')}" if is_hint else "🌊 Celeste"
        else:
            cls = "student"
            label = "🧑‍🔬 Student"
        msgs_html += f'<div class="msg {cls}"><div class="msg-label">{label}</div><div class="msg-body">{content}</div></div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>Sky Tutor — Celeste · Session Report</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; background:#0b1120; color:#e6edf3; margin:0; padding:0; }}
  .container {{ max-width:800px; margin:0 auto; padding:30px 20px; }}
  header {{ text-align:center; margin-bottom:30px; }}
  header h1 {{ color:#6dd5ed; margin:0; }}
  header p {{ color:#8b949e; }}
  .meta {{ display:flex; gap:12px; justify-content:center; flex-wrap:wrap; }}
  .tag {{ background:#161b22; border:1px solid #30363d; border-radius:6px; padding:4px 10px; font-size:0.8rem; }}
  .scenario-info {{ background:#161b22; border:1px solid #3a7bd5; border-radius:10px; padding:14px 18px; margin-bottom:20px; }}
  .chat-log {{ display:flex; flex-direction:column; gap:12px; }}
  .msg {{ padding:12px 16px; border-radius:10px; }}
  .msg-label {{ font-size:0.75rem; font-weight:600; margin-bottom:4px; }}
  .celeste {{ background:#1c2333; border:1px solid #30363d; }}
  .student {{ background:#0d2818; border:1px solid #3fb950; }}
  .hint {{ background:#2d1b00; border:1px solid #d29922; }}
  .score-card {{ background:#161b22; border:1px solid #6dd5ed; border-radius:10px; padding:20px; margin-top:20px; }}
  .score-card h3 {{ color:#6dd5ed; margin-top:0; }}
  .score-card table {{ width:100%; border-collapse:collapse; }}
  .score-card td {{ padding:6px 10px; border-bottom:1px solid #30363d; }}
  .score-val {{ text-align:right; font-weight:600; color:#6dd5ed; }}
  .score-total {{ font-size:1.2rem; font-weight:700; color:#6dd5ed; margin-top:10px; text-align:right; }}
  .feedback {{ font-size:0.85rem; color:#8b949e; margin-top:8px; padding:10px 12px;
                background:#0d2818; border:1px solid #3fb950; border-radius:8px; }}
  footer {{ text-align:center; color:#8b949e; font-size:0.75rem; margin-top:40px; padding-top:20px; border-top:1px solid #30363d; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>🌊 Sky Tutor — Celeste</h1>
    <p>Reverse Tutor · Atmospheric Optics · Session Transcript</p>
    <div class="meta">
      <span class="tag">📅 {now}</span>
      <span class="tag">🤖 {model}</span>
      <span class="tag">💡 Hints used: {hints_used}</span>
      <span class="tag">📊 Final conviction: {conviction}/100</span>
      <span class="tag">{'✅ Celeste Convinced' if scores else '❌ Not yet convinced'}</span>
    </div>
  </header>

  <div class="scenario-info">
    <strong>Topic:</strong> Why is the sky blue?<br>
    <strong>Misconception:</strong> The sky reflects the ocean's blue colour.<br>
    <strong>Correct answer:</strong> Rayleigh scattering of shorter-wavelength sunlight by atmospheric gas molecules.
  </div>

  <div class="chat-log">
    {msgs_html}
  </div>

  {score_html}

  <footer>Generated by Sky Tutor — Celeste · {now}</footer>
</div>
</body>
</html>"""


# ========== SESSION INIT ==========

MODELS = {
    "gpt-4o-mini": "GPT-4o Mini (Default)",
    "gpt-4o":      "GPT-4o (Smarter, slower)",
}

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    selected_model = st.selectbox("Model", list(MODELS.keys()), format_func=lambda x: MODELS[x])


def _init_bot():
    st.session_state.bot = SkyTutor(selected_model)
    st.session_state.messages = []
    st.session_state.scores = None
    st.session_state.conviction = 95
    st.session_state.active_model = selected_model


if "bot" not in st.session_state:
    _init_bot()

if st.session_state.get("active_model") != selected_model:
    _init_bot()
    st.rerun()

# ---- Opening statement ----
if not st.session_state.messages:
    trigger = (
        "Begin by introducing yourself (you're Celeste, a passionate science enthusiast) "
        "and asserting your misconception about why the sky is blue. Keep it to 3–4 sentences. "
        "Be warm and enthusiastic. End with your conviction tag."
    )
    try:
        client = st.session_state.bot.client
        comp = client.chat.completions.create(
            model=st.session_state.bot.model,
            messages=[
                {"role": "system", "content": st.session_state.bot.system_prompt},
                {"role": "user",   "content": trigger},
            ],
            temperature=0.7,
            max_tokens=250,
        )
        raw_opening = comp.choices[0].message.content.strip()
        clean_opening, conv = parse_conviction(raw_opening)
        if conv is not None:
            st.session_state.conviction = conv

        st.session_state.bot.conversation_history.append({"role": "user",      "content": trigger})
        st.session_state.bot.conversation_history.append({"role": "assistant", "content": raw_opening})
        st.session_state.messages.append({"role": "assistant", "content": clean_opening})
    except Exception as e:
        st.session_state.messages.append({"role": "assistant", "content": f"❌ Error: {e}"})
    st.rerun()

bot = st.session_state.bot

# ========== TITLE ==========
st.markdown("""
<div class="title-bar">
    <div class="icon">🌊</div>
    <div>
        <h1>Sky Tutor — Celeste</h1>
        <p class="subtitle">Reverse Tutor AI · Atmospheric Optics · Why Is the Sky Blue?</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- Topic info box ----
st.markdown(f"""
<div class="scenario-box">
    <div class="scenario-label">Active Topic</div>
    <strong>Why is the sky blue?</strong><br>
    <span style="color:#8b949e;">
        Celeste's claim: the sky reflects the ocean &nbsp;|&nbsp;
        Reality: Rayleigh scattering of short-wavelength sunlight
    </span>
</div>
""", unsafe_allow_html=True)

# ---- Conviction meter ----
render_conviction_meter(st.session_state.conviction)

# ---- Student briefing box ----
st.markdown(f"""
<div class="briefing-box">
    <h4>📋 Your Task</h4>
    <p>{SCENARIO['briefing']}</p>
    <p style="color: var(--text-secondary); margin-top: 8px; font-size: 0.82rem;">
        <strong>Tip:</strong> Celeste won't accept bare assertions like "it's scattering."
        Explain <em>what</em> scattering is, <em>why</em> shorter wavelengths scatter more,
        and <em>why</em> we see blue specifically (not violet). Or poke logical holes in her
        ocean-mirror theory until it falls apart.
    </p>
</div>
""", unsafe_allow_html=True)

# ---- Win state ----
if st.session_state.conviction <= 15 or bot.conceded:
    st.markdown("""
    <div class="win-banner">
        <div style="font-size:3.5rem;">🎓</div>
        <h2>You did it!</h2>
        <p>You convinced Celeste that the sky is blue due to Rayleigh scattering,
        not ocean reflection. Science wins!</p>
    </div>
    """, unsafe_allow_html=True)

# ========== CHAT DISPLAY ==========
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        is_hint = msg.get("is_hint", False)
        if msg["role"] == "assistant":
            avatar = "💡" if is_hint else "🌊"
            with st.chat_message("assistant", avatar=avatar):
                text = msg["content"]
                if "---GRADE---" in text:
                    parts = text.split("---GRADE---")
                    st.write(parts[0].strip())
                    if st.session_state.scores:
                        s = st.session_state.scores
                        cats = ["Logic", "Physics", "Clarity", "Persuasion"]
                        rows = "".join(f"""<tr>
                            <td style="padding:6px 10px;border-bottom:1px solid #30363d;">{c}</td>
                            <td style="padding:6px 10px;border-bottom:1px solid #30363d;text-align:right;
                                       font-weight:600;color:#6dd5ed;">{s.get(c,'—')}</td>
                        </tr>""" for c in cats)
                        st.markdown(f"""<div style="background:#161b22;border:1px solid #6dd5ed;
                            border-radius:10px;padding:16px;margin:10px 0;">
                            <h3 style="color:#6dd5ed;margin-top:0;">📊 Performance Report</h3>
                            <table style="width:100%;border-collapse:collapse;">{rows}</table>
                            <div style="font-size:1.2rem;font-weight:700;color:#6dd5ed;margin-top:10px;
                                        text-align:right;">{s.get("Total","—")}</div>
                            <div style="font-size:0.85rem;color:#8b949e;margin-top:8px;padding:10px 12px;
                                        background:#0d2818;border:1px solid #3fb950;border-radius:8px;">
                                💬 {s.get("Feedback","")}
                            </div>
                        </div>""", unsafe_allow_html=True)
                    if len(parts) > 1 and "---END GRADE---" in parts[1]:
                        after = parts[1].split("---END GRADE---")
                        if len(after) > 1 and after[1].strip():
                            st.write(after[1].strip())
                else:
                    st.write(text)
        else:
            with st.chat_message("user"):
                st.write(msg["content"])

# ========== INPUT ROW ==========
hints_left = MAX_HINTS - bot.hints_used
col_chat, col_hint = st.columns([5, 1])

with col_chat:
    if prompt := st.chat_input("Challenge Celeste's theory..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        raw_response = bot.get_response(prompt)

        # Parse conviction
        clean_response, new_conviction = parse_conviction(raw_response)
        if new_conviction is not None:
            st.session_state.conviction = new_conviction

        st.session_state.messages.append({"role": "assistant", "content": clean_response})

        if "---GRADE---" in raw_response and not st.session_state.scores:
            st.session_state.scores = bot.parse_grade(raw_response)

        st.rerun()

with col_hint:
    hint_disabled = hints_left <= 0 or bot.conceded
    hint_label = f"💡 Hint ({hints_left})" if hints_left > 0 else "💡 No hints"
    if st.button(hint_label, disabled=hint_disabled, use_container_width=True):
        raw_hint = bot.get_response("", is_hint_request=True)
        clean_hint, hint_conv = parse_conviction(raw_hint)
        if hint_conv is not None:
            st.session_state.conviction = hint_conv
        st.session_state.messages.append({
            "role": "assistant",
            "content": clean_hint,
            "is_hint": True,
            "hint_num": bot.hints_used,
        })
        st.rerun()

# ========== SIDEBAR ==========
with st.sidebar:
    st.divider()
    st.markdown("### 📊 Session")

    conceded_val = "✅ Yes!" if bot.conceded else "❌ Not yet"
    hint_val = f"{bot.hints_used} / {MAX_HINTS}"
    msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])
    conv = st.session_state.conviction
    stage = get_conviction_stage(conv)

    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Celeste Convinced</div>
        <div class="metric-value">{conceded_val}</div>
    </div>
    <div class="metric-box">
        <div class="metric-label">Conviction</div>
        <div class="metric-value" style="color:{stage['color']};">{conv}/100 {stage['emoji']}</div>
    </div>
    <div class="metric-box">
        <div class="metric-label">Hints Used</div>
        <div class="metric-value">{hint_val}</div>
    </div>
    <div class="metric-box">
        <div class="metric-label">Your Responses</div>
        <div class="metric-value">{msg_count}</div>
    </div>
    """, unsafe_allow_html=True)

    if bot.conceded:
        st.success("🎉 You convinced Celeste!")
        st.balloons()

    st.divider()
    st.markdown("### 🔐 Security")
    st.markdown('<div class="status-badge status-active">🔒 Secured</div>', unsafe_allow_html=True)
    st.caption("Copy/paste & right-click are disabled.")

    st.divider()
    st.markdown("### 🛠 Controls")

    if st.button("🔄 Reset Chat", use_container_width=True):
        _init_bot()
        st.rerun()

    if st.button("📄 Export HTML Report", use_container_width=True):
        html_content = build_html_export(
            st.session_state.messages,
            st.session_state.scores,
            selected_model,
            bot.hints_used,
            st.session_state.conviction,
        )
        st.download_button(
            label="⬇️ Download Report",
            data=html_content,
            file_name=f"celeste_session_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
            mime="text/html",
            use_container_width=True,
        )

    if st.button("💾 Export JSON", use_container_width=True):
        export_data = {
            "model": selected_model,
            "topic": "Why is the sky blue?",
            "conversation": st.session_state.messages,
            "scores": st.session_state.scores,
            "hints_used": bot.hints_used,
            "conviction": st.session_state.conviction,
            "timestamp": datetime.now().isoformat(),
            "bot_conceded": bot.conceded,
        }
        st.download_button(
            label="⬇️ Download JSON",
            data=json.dumps(export_data, indent=2),
            file_name=f"celeste_session_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True,
        )

    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
