import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import json
from datetime import datetime

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="Barrier Navigator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
    --bg:        #0d1117;
    --surface:   #161b22;
    --surface2:  #1c2330;
    --border:    #30363d;
    --accent:    #d2a8ff;
    --accent2:   #f78166;
    --warn:      #e3b341;
    --text:      #e6edf3;
    --muted:     #8b949e;
    --user-bg:   #2d1f45;
    --bot-bg:    #1c2330;
    --hint-bg:   #1a2a1a;
    --hint-border:#3fb950;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; max-width: 1100px; }

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

.title-bar {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 18px 24px;
    background: linear-gradient(135deg, #1a0533, #2d1254, #1a2a45);
    border: 1px solid var(--border);
    border-radius: 12px;
    margin-bottom: 20px;
}
.title-bar .icon { font-size: 2.4rem; }
.title-bar h1 {
    font-family: 'Syne', sans-serif;
    font-size: 1.7rem;
    font-weight: 800;
    margin: 0;
    background: linear-gradient(90deg, #d2a8ff, #bf91f3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.title-bar .subtitle {
    font-size: 0.78rem;
    color: var(--muted);
    margin: 0;
    font-weight: 300;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.status-active  { background: #0d2818; border: 1px solid #3fb950; color: #3fb950; }
.status-pending { background: #2d1f0a; border: 1px solid var(--warn); color: var(--warn); }

.chat-wrap {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 8px 4px;
}
.msg-row {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    animation: fadeUp 0.3s ease both;
}
.msg-row.user  { flex-direction: row-reverse; }

@keyframes fadeUp {
    from { opacity:0; transform: translateY(10px); }
    to   { opacity:1; transform: translateY(0); }
}

.avatar {
    width: 36px; height: 36px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; flex-shrink: 0;
}
.avatar-bot  { background: linear-gradient(135deg,#2d1254,#5a189a); border: 2px solid var(--accent); }
.avatar-user { background: linear-gradient(135deg,#3a1a2a,#7b2d4a); border: 2px solid var(--accent2); }

.bubble {
    max-width: 72%;
    padding: 12px 16px;
    border-radius: 14px;
    font-size: 0.93rem;
    line-height: 1.6;
}
.bubble-bot  {
    background: var(--bot-bg);
    border: 1px solid var(--border);
    border-top-left-radius: 4px;
}
.bubble-user {
    background: var(--user-bg);
    border: 1px solid #5a2d8e;
    border-top-right-radius: 4px;
}
.bubble-hint {
    background: var(--hint-bg);
    border: 1px solid var(--hint-border);
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 0.88rem;
    color: #7ee787;
}
.hint-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--hint-border);
    font-weight: 700;
    margin-bottom: 4px;
}

.score-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin-top: 10px;
}
.score-card h3 {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    color: var(--accent);
    margin-bottom: 14px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.score-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 7px 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.88rem;
}
.score-row:last-child { border-bottom: none; }
.score-val {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    color: #3fb950;
}
.score-total {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--accent);
    text-align: center;
    padding-top: 10px;
}

.metric-box {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.metric-label { font-size: 0.72rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; }
.metric-value { font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 700; }

.stButton > button {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

[data-testid="stChatInput"] textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(210,168,255,0.15) !important;
}

hr { border-color: var(--border) !important; }

[data-testid="stSelectbox"] > div > div {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}

.chat-wrap * {
    -webkit-user-select: none !important;
    -moz-user-select: none !important;
    user-select: none !important;
}
textarea, input {
    -webkit-user-select: auto !important;
    user-select: auto !important;
}

[data-testid="stDownloadButton"] button {
    width: 100%;
    background: linear-gradient(135deg, #2d1254, #5a189a) !important;
    border-color: var(--accent) !important;
    color: var(--text) !important;
}

.scenario-box {
    background: #1a1230;
    border: 1px solid #5a189a;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 16px;
    font-size: 0.88rem;
    color: #d2a8ff;
}
.scenario-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8b949e;
    font-weight: 700;
    margin-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)

# ========== ANTI-CHEAT JS ==========
components.html("""
<script>
const parentDoc = window.parent.document;
parentDoc.addEventListener('copy',        e => { e.preventDefault(); e.stopPropagation(); }, true);
parentDoc.addEventListener('paste',       e => { e.preventDefault(); e.stopPropagation(); }, true);
parentDoc.addEventListener('contextmenu', e => { e.preventDefault(); e.stopPropagation(); }, true);
</script>
""", height=0, width=0)

# ========== AUTH ==========
if "OPENAI_API_KEY" not in st.secrets:
    st.error("Missing OpenAI API Key in secrets."); st.stop()
if "APP_PASSWORD" not in st.secrets:
    st.error("Missing APP_PASSWORD in secrets."); st.stop()

def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("### 🔒 Access Required")
        st.text_input("Enter access password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Enter access password", type="password", on_change=password_entered, key="password")
        st.error("Incorrect password — try again.")
        return False
    return True

if not check_password():
    st.stop()

# ========== SCENARIOS ==========
SCENARIOS = {
    "IV nanoparticle → tumour": {
        "drug": "Doxorubicin-loaded PEGylated liposome (100 nm)",
        "route": "Intravenous (IV)",
        "target": "solid tumour (breast cancer)",
        "barriers": [
            "protein corona formation & opsonisation",
            "MPS clearance (liver Kupffer cells, spleen)",
            "lung capillary filtration (>2 µm blocked)",
            "renal filtration (>6 nm / >60 kDa retained)",
            "tumour endothelium extravasation (<300 nm fenestrations)",
            "glycocalyx on endothelial surface",
            "tumour interstitial pressure & ECM",
            "cellular uptake & endosomal escape",
        ],
        "misconception": "A PEGylated liposome encapsulating doxorubicin is 100 nm — perfect size! Once you inject it IV, it should sail straight to the tumour. PEGylation is basically a stealth coat, so the immune system won't even notice it. Job done.",
    },
    "Oral insulin": {
        "drug": "Insulin nanoparticle (pH-responsive polymer, 200 nm)",
        "route": "Oral",
        "target": "systemic bloodstream (via small intestine)",
        "barriers": [
            "gastric acid degradation (pH 1–3.5) & pepsin",
            "mucus layer clearance (replaced every 4–5 h)",
            "epithelial cell membrane (transcytosis required for nanoparticles)",
            "tight junctions (paracellular blocked for >2 nm particles)",
            "first-pass hepatic metabolism",
            "BCS classification & solubility/permeability challenges",
        ],
        "misconception": "If you just coat insulin in a pH-responsive nanoparticle, the stomach acid won't touch it, and then it pops open in the small intestine. Plenty of surface area there — it should absorb fine, just like a small molecule drug.",
    },
    "Transdermal peptide patch": {
        "drug": "GLP-1 analogue peptide (3.8 kDa) in a patch",
        "route": "Transdermal",
        "target": "systemic bloodstream (via dermis vasculature)",
        "barriers": [
            "stratum corneum (lipid-rich dead keratinocytes, ~500 Da / lipophilic cutoff)",
            "viable epidermis cell layers",
            "dermis extracellular matrix (collagen gel, 3–5 mm)",
            "dermal vasculature uptake vs. lymphatic drainage",
            "peptide molecular weight (>>500 Da, hydrophilic)",
            "enzymatic degradation in skin",
        ],
        "misconception": "A GLP-1 peptide patch sounds ideal — no injections, just stick it on. The skin is just a thin layer; if the patch delivers enough drug, it should diffuse right through and get into the blood.",
    },
}

# ========== BOT CLASS ==========
MAX_HINTS = 3

class BarrierNavigator:
    def __init__(self, model_name="gpt-4o", scenario_key=None):
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        self.model = model_name
        self.conceded = False
        self.hints_used = 0
        self.conversation_history = []
        self.scenario_key = scenario_key or list(SCENARIOS.keys())[0]
        sc = SCENARIOS[self.scenario_key]

        barriers_numbered = "\n".join(
            f"  {i+1}. {b}" for i, b in enumerate(sc["barriers"])
        )

        self.system_prompt = f"""# PERSONA
You are "Barrier-Blind Boris," a Reverse Tutor AI. You are enthusiastic about drug delivery but dismissive of biological barriers. You believe the drug just needs to be delivered by the right route and it will reach its target — barriers are minor inconveniences at most. You argue confidently but will concede when the student explains the barriers clearly and specifically.

# SCENARIO
Drug/Formulation: {sc['drug']}
Route of administration: {sc['route']}
Intended target: {sc['target']}

# YOUR MISCONCEPTION (assert this at the start)
"{sc['misconception']}"

# BARRIERS THE STUDENT MUST IDENTIFY
The following biological barriers exist along this route. The student must correctly explain at least FOUR of these to trigger your concession:
{barriers_numbered}

# RULES OF ENGAGEMENT
- Keep replies SHORT (2–4 sentences). Stay in character — sceptical, slightly dismissive of each barrier the student raises.
- For each barrier the student correctly identifies and explains, briefly push back once ("But surely that's not a big deal because...") before accepting that point.
- Track internally how many distinct barriers the student has correctly explained. Do NOT reveal this count.
- No lecturing, no volunteering information, no hints unless specifically triggered.

# HINT HANDLING
When the student requests a hint, give ONE short Socratic nudge pointing toward one unstated barrier WITHOUT naming it directly. Never repeat a previous hint. Maximum {MAX_HINTS} hints total.

# CONCESSION TRIGGER
When the student has correctly explained at least FOUR distinct barriers from the list above, concede. Say EXACTLY:
"Alright, I give in — there are clearly far more checkpoints between injection and target than I appreciated. The body is not a simple pipe."

Then immediately output a grading block in this EXACT format:

---GRADE---
Breadth: X/5
Accuracy: X/5
Mechanism: X/5
Communication: X/5
Total: XX/20
Feedback: [2 sentences: one strength + one improvement suggestion]
---END GRADE---

# POST-CONCESSION
After grading, ask: "Which of these barriers do you think is the single hardest engineering problem to solve when designing the next generation of nanocarriers — and why?"
"""

    def get_response(self, user_message, is_hint_request=False):
        messages = [{"role": "system", "content": self.system_prompt}]
        for msg in self.conversation_history:
            messages.append({"role": msg["role"], "content": msg["content"]})

        if is_hint_request:
            hint_prompt = (
                f"The student is requesting hint #{self.hints_used + 1}. "
                "Give a short Socratic nudge (1–2 sentences) pointing toward one barrier they haven't mentioned yet, "
                "without naming it directly. Don't repeat previous hints."
            )
            messages.append({"role": "user", "content": hint_prompt})
        else:
            messages.append({"role": "user", "content": user_message})

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=400
            )
            ai_response = completion.choices[0].message.content.strip()

            if is_hint_request:
                self.hints_used += 1
                self.conversation_history.append({"role": "user", "content": f"[Hint request #{self.hints_used}]"})
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
                for cat in ["Breadth", "Accuracy", "Mechanism", "Communication", "Total"]:
                    if line.startswith(f"{cat}:"):
                        scores[cat] = line.split(":")[1].strip()
                if line.startswith("Feedback:"):
                    scores["Feedback"] = line.split(":", 1)[1].strip()
            return scores
        except Exception:
            return None


# ========== HTML EXPORT ==========
def build_html_export(messages, scores, model, hints_used, scenario_key):
    now = datetime.now().strftime("%B %d, %Y – %H:%M")
    sc = SCENARIOS.get(scenario_key, {})
    score_html = ""
    if scores:
        cats = ["Breadth", "Accuracy", "Mechanism", "Communication"]
        rows = "".join(f"""
            <tr>
                <td>{c}</td>
                <td class="score-val">{scores.get(c,'—')}</td>
                <td><div class="bar"><div class="bar-fill" style="width:{int(scores.get(c,'0/5').split('/')[0])*20}%"></div></div></td>
            </tr>""" for c in cats)
        total = scores.get("Total", "—")
        feedback = scores.get("Feedback", "")
        score_html = f"""
        <div class="score-section">
            <h2>📊 Performance Report</h2>
            <table>
                <thead><tr><th>Category</th><th>Score</th><th>Visual</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
            <div class="total-score">Total: {total}</div>
            <div class="feedback-box">💬 {feedback}</div>
        </div>"""

    msgs_html = ""
    for m in messages:
        role_class = "user" if m["role"] == "user" else "bot"
        role_label = "You" if m["role"] == "user" else "🧱 Boris"
        content = m["content"]
        if "---GRADE---" in content:
            content = content.split("---GRADE---")[0].strip()
        if m.get("is_hint"):
            msgs_html += f'<div class="msg hint-msg"><span class="hint-tag">💡 Hint #{m.get("hint_num","")}:</span> {content}</div>'
        else:
            msgs_html += f'<div class="msg {role_class}"><span class="role-tag">{role_label}</span><p>{content}</p></div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Barrier Navigator – {now}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:'DM Sans',sans-serif; background:#0d1117; color:#e6edf3; padding:40px 20px; }}
  .container {{ max-width:780px; margin:auto; }}
  header {{ text-align:center; margin-bottom:36px; }}
  header h1 {{ font-family:'Syne',sans-serif; font-size:2rem; font-weight:800;
               background:linear-gradient(90deg,#d2a8ff,#bf91f3);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
  header p {{ color:#8b949e; font-size:0.85rem; margin-top:6px; }}
  .meta {{ display:flex; gap:12px; justify-content:center; flex-wrap:wrap; margin-top:12px; }}
  .tag {{ background:#1c2330; border:1px solid #30363d; border-radius:20px;
          padding:4px 14px; font-size:0.75rem; color:#8b949e; }}
  .scenario-info {{ background:#1a1230; border:1px solid #5a189a; border-radius:10px;
                    padding:14px 18px; margin-bottom:24px; font-size:0.88rem; color:#d2a8ff; }}
  .chat-log {{ display:flex; flex-direction:column; gap:14px; margin:28px 0; }}
  .msg {{ padding:14px 18px; border-radius:14px; font-size:0.93rem; line-height:1.65; }}
  .msg .role-tag {{ font-size:0.72rem; text-transform:uppercase; letter-spacing:0.07em;
                    font-weight:700; display:block; margin-bottom:5px; }}
  .bot  {{ background:#1c2330; border:1px solid #30363d; border-top-left-radius:4px; }}
  .bot .role-tag {{ color:#d2a8ff; }}
  .user {{ background:#2d1f45; border:1px solid #5a2d8e; border-top-right-radius:4px; margin-left:60px; }}
  .user .role-tag {{ color:#f78166; }}
  .hint-msg {{ background:#1a2a1a; border:1px solid #3fb950; border-radius:10px;
               font-size:0.88rem; color:#7ee787; padding:12px 16px; }}
  .hint-tag {{ font-weight:700; margin-right:6px; }}
  .score-section {{ background:#161b22; border:1px solid #30363d; border-radius:14px; padding:24px; margin-top:30px; }}
  .score-section h2 {{ font-family:'Syne',sans-serif; font-size:1.1rem; color:#d2a8ff; margin-bottom:18px; }}
  table {{ width:100%; border-collapse:collapse; }}
  th {{ text-align:left; font-size:0.75rem; text-transform:uppercase; color:#8b949e; padding:6px 0; }}
  td {{ padding:9px 0; border-bottom:1px solid #30363d; font-size:0.9rem; }}
  td.score-val {{ font-family:'Syne',sans-serif; font-weight:700; color:#3fb950; width:60px; }}
  .bar {{ background:#30363d; border-radius:4px; height:8px; width:180px; overflow:hidden; }}
  .bar-fill {{ background:linear-gradient(90deg,#d2a8ff,#3fb950); height:100%; border-radius:4px; }}
  .total-score {{ font-family:'Syne',sans-serif; font-size:2rem; font-weight:800;
                  color:#d2a8ff; text-align:center; padding:18px 0 8px; }}
  .feedback-box {{ background:#0d2818; border:1px solid #3fb950; border-radius:8px;
                   padding:12px 16px; color:#7ee787; font-size:0.9rem; margin-top:8px; }}
  footer {{ text-align:center; color:#8b949e; font-size:0.75rem; margin-top:40px; padding-top:20px; border-top:1px solid #30363d; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>🧱 Barrier Navigator</h1>
    <p>AI Reverse Tutor — Session Transcript</p>
    <div class="meta">
      <span class="tag">📅 {now}</span>
      <span class="tag">🤖 {model}</span>
      <span class="tag">💡 Hints used: {hints_used}</span>
      <span class="tag">{'✅ Boris Convinced' if scores else '❌ Not yet convinced'}</span>
    </div>
  </header>

  <div class="scenario-info">
    <strong>Scenario:</strong> {scenario_key}<br>
    <strong>Drug:</strong> {sc.get('drug','')}<br>
    <strong>Route:</strong> {sc.get('route','')} → <strong>Target:</strong> {sc.get('target','')}
  </div>

  <div class="chat-log">
    {msgs_html}
  </div>

  {score_html}

  <footer>Generated by Barrier Navigator · {now}</footer>
</div>
</body>
</html>"""


# ========== SESSION INIT ==========
MODELS = {
    "gpt-4o":      "GPT-4o (Recommended)",
    "gpt-4o-mini": "GPT-4o Mini (Faster)",
}

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    selected_model = st.selectbox("Model", list(MODELS.keys()), format_func=lambda x: MODELS[x])
    st.markdown("### 🧪 Scenario")
    selected_scenario = st.selectbox("Drug delivery scenario", list(SCENARIOS.keys()))

def _init_bot():
    st.session_state.bot = BarrierNavigator(selected_model, selected_scenario)
    st.session_state.messages = []
    st.session_state.scores = None
    st.session_state.active_scenario = selected_scenario
    st.session_state.active_model = selected_model

if "bot" not in st.session_state:
    _init_bot()

# Re-init if model or scenario changed
if (st.session_state.get("active_model") != selected_model or
        st.session_state.get("active_scenario") != selected_scenario):
    _init_bot()
    st.rerun()

# ---- Opening statement ----
if not st.session_state.messages:
    trigger = "Begin by asserting your misconception about this delivery scenario, as instructed. Keep it to 2–3 sentences."
    try:
        client = st.session_state.bot.client
        comp = client.chat.completions.create(
            model=st.session_state.bot.model,
            messages=[
                {"role": "system", "content": st.session_state.bot.system_prompt},
                {"role": "user",   "content": trigger}
            ],
            temperature=0.7, max_tokens=200
        )
        opening = comp.choices[0].message.content.strip()
        st.session_state.bot.conversation_history.append({"role": "user",      "content": trigger})
        st.session_state.bot.conversation_history.append({"role": "assistant", "content": opening})
        st.session_state.messages.append({"role": "assistant", "content": opening})
    except Exception as e:
        st.session_state.messages.append({"role": "assistant", "content": f"❌ Error: {e}"})
    st.rerun()

bot = st.session_state.bot
sc  = SCENARIOS[selected_scenario]

# ========== TITLE ==========
st.markdown("""
<div class="title-bar">
    <div class="icon">🧱</div>
    <div>
        <h1>Barrier Navigator</h1>
        <p class="subtitle">Reverse Tutor AI · Drug Delivery Barriers & Routes of Administration</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- Scenario info box ----
st.markdown(f"""
<div class="scenario-box">
    <div class="scenario-label">Active Scenario</div>
    <strong>{selected_scenario}</strong><br>
    <span style="color:#8b949e;">Drug: {sc['drug']} &nbsp;|&nbsp; Route: {sc['route']} &nbsp;→&nbsp; Target: {sc['target']}</span>
</div>
""", unsafe_allow_html=True)

# ========== CHAT DISPLAY ==========
chat_html_parts = []
for msg in st.session_state.messages:
    role    = msg["role"]
    content = msg["content"]
    display_content = content.split("---GRADE---")[0].strip() if "---GRADE---" in content else content

    if msg.get("is_hint"):
        chat_html_parts.append(f"""
        <div class="msg-row">
            <div class="avatar avatar-bot">💡</div>
            <div class="bubble-hint">
                <div class="hint-label">Hint #{msg.get('hint_num','')}</div>
                {display_content}
            </div>
        </div>""")
    elif role == "assistant":
        chat_html_parts.append(f"""
        <div class="msg-row">
            <div class="avatar avatar-bot">🧱</div>
            <div class="bubble bubble-bot">{display_content}</div>
        </div>""")
    else:
        chat_html_parts.append(f"""
        <div class="msg-row user">
            <div class="avatar avatar-user">👤</div>
            <div class="bubble bubble-user">{display_content}</div>
        </div>""")

st.markdown(f'<div class="chat-wrap">{"".join(chat_html_parts)}</div>', unsafe_allow_html=True)

# ---- Inline score card after concession ----
if bot.conceded and st.session_state.scores:
    s    = st.session_state.scores
    cats = ["Breadth", "Accuracy", "Mechanism", "Communication"]
    rows = "".join(
        f'<div class="score-row"><span>{c}</span><span class="score-val">{s.get(c,"—")}</span></div>'
        for c in cats
    )
    st.markdown(f"""
    <div class="score-card">
        <h3>📊 Performance Report</h3>
        {rows}
        <div class="score-total">{s.get("Total","—")}</div>
        <div style="font-size:0.85rem;color:#8b949e;margin-top:8px;padding:10px 12px;
                    background:#0d2818;border:1px solid #3fb950;border-radius:8px;">
            💬 {s.get("Feedback","")}
        </div>
    </div>""", unsafe_allow_html=True)

# ========== INPUT ROW ==========
hints_left = MAX_HINTS - bot.hints_used
col_chat, col_hint = st.columns([5, 1])

with col_chat:
    if prompt := st.chat_input("Name and explain a barrier to Boris..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = bot.get_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        if "---GRADE---" in response and not st.session_state.scores:
            st.session_state.scores = bot.parse_grade(response)
        st.rerun()

with col_hint:
    hint_disabled = hints_left <= 0 or bot.conceded
    hint_label = f"💡 Hint ({hints_left})" if hints_left > 0 else "💡 No hints"
    if st.button(hint_label, disabled=hint_disabled, use_container_width=True):
        hint_response = bot.get_response("", is_hint_request=True)
        st.session_state.messages.append({
            "role": "assistant",
            "content": hint_response,
            "is_hint": True,
            "hint_num": bot.hints_used
        })
        st.rerun()

# ========== SIDEBAR ==========
with st.sidebar:
    st.divider()
    st.markdown("### 📊 Session")

    conceded_val = "✅ Yes!" if bot.conceded else "❌ Not yet"
    hint_val     = f"{bot.hints_used} / {MAX_HINTS}"
    msg_count    = len([m for m in st.session_state.messages if m["role"] == "user"])

    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Boris Convinced</div>
        <div class="metric-value">{conceded_val}</div>
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
        st.success("🎉 You convinced Boris!")
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
            selected_scenario
        )
        st.download_button(
            label="⬇️ Download Report",
            data=html_content,
            file_name=f"barrier_session_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
            mime="text/html",
            use_container_width=True
        )

    if st.button("💾 Export JSON", use_container_width=True):
        export_data = {
            "model": selected_model,
            "scenario": selected_scenario,
            "conversation": st.session_state.messages,
            "scores": st.session_state.scores,
            "hints_used": bot.hints_used,
            "timestamp": datetime.now().isoformat(),
            "bot_conceded": bot.conceded
        }
        st.download_button(
            label="⬇️ Download JSON",
            data=json.dumps(export_data, indent=2),
            file_name=f"barrier_session_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True
        )

    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
