import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import json
from datetime import datetime

# ========== CONFIGURATION & AUTHENTICATION ==========
st.set_page_config(page_title="Barrier Navigator", layout="wide")

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
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --bg-tertiary: #1c2333;
    --border: #30363d;
    --text-primary: #e6edf3;
    --text-secondary: #8b949e;
    --accent: #a371f7;
    --accent-dim: #6e40c9;
    --success: #3fb950;
    --warning: #d29922;
    --danger: #f85149;
}

.stApp { background-color: var(--bg-primary); color: var(--text-primary); }

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
    background: linear-gradient(135deg, #1a1230 0%, #161b22 100%);
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

.status-badge {
    display: inline-block; font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem; padding: 4px 10px; border-radius: 6px;
}
.status-active {
    background: #0d2818; border: 1px solid #3fb950; color: #3fb950;
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
        "briefing": "Boris believes that a 100 nm PEGylated liposome injected IV will cruise straight to the tumour unopposed. Your job is to explain the biological barriers it actually faces between the injection site and the cancer cell cytoplasm. Name and *explain the mechanism* of each barrier — don't just list them.",
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
        "briefing": "Boris thinks a pH-responsive nanoparticle is all you need to deliver insulin orally. Your job is to explain the biological barriers between swallowing the pill and getting insulin into the bloodstream. For each barrier, explain *why* it blocks this specific formulation — don't just name it.",
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
        "briefing": "Boris thinks a transdermal patch for a 3.8 kDa peptide is straightforward — just stick it on and it diffuses through. Your job is to explain which skin and tissue barriers prevent passive delivery of this peptide. Explain the *mechanism* of each barrier, not just the name.",
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
- For each barrier the student raises with little or no explanation, push back once asking for more detail. If they have already given a clear mechanistic explanation, accept it directly without mandatory pushback.
- Track internally how many distinct barriers the student has correctly explained. Do NOT reveal this count.
- No lecturing, no volunteering information, no hints unless specifically triggered.

# CONCESSION DIFFICULTY — BE SCEPTICAL BUT FAIR
- Do NOT concede just because the student names a barrier with no explanation at all. They should explain at least the basic mechanism: what the barrier does and why it matters for this drug/formulation.
- If a student gives only a bare name (e.g. "mucus is a barrier" with nothing else), push back once asking for more detail.
- Once the student provides a reasonable mechanistic explanation — even if not exhaustive — accept that barrier and move on. Do NOT keep demanding more detail once a clear mechanism has been given.
- A good-enough explanation covers: what the barrier physically does AND why it is relevant to this drug or formulation. A perfect textbook answer is NOT required.
- Phrases like "OK, fair point" or "I'll grant you that one" should appear as soon as the student gives a coherent mechanistic explanation.
- When a student asks "what should I argue?" or "what is the question?" — restate your misconception clearly and tell them their task is to show you why you're wrong by explaining specific biological barriers. Do NOT hint at what those barriers are.

# HINT HANDLING
When the student requests a hint, give ONE short Socratic nudge pointing toward one unstated barrier WITHOUT naming it directly. Never repeat a previous hint. Maximum {MAX_HINTS} hints total.

# CONCESSION TRIGGER
When the student has correctly explained (with mechanism) at least FOUR distinct barriers from the list above, concede. Say EXACTLY:
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

# GRADING RUBRIC — ANCHORED SCORING
Use these anchors. Do NOT default to high scores.

**Breadth (how many distinct barriers identified):**
  1 = 1 barrier | 2 = 2 barriers | 3 = 3 barriers | 4 = 4 barriers | 5 = 5+ barriers

**Accuracy (scientific correctness of what was stated):**
  1 = mostly wrong or confused | 2 = some correct points but significant errors | 3 = largely correct, minor errors | 4 = correct with only trivial imprecisions | 5 = fully correct, no errors

**Mechanism (depth of mechanistic explanation):**
  1 = barriers named only, no mechanism | 2 = vague mechanism for some | 3 = clear mechanism for some, vague for others | 4 = clear mechanism for most, with physicochemical reasoning | 5 = every barrier explained with specific mechanism AND linked to this drug/formulation's properties

**Communication (clarity, structure, and tone):**
  1 = incoherent or rude | 2 = understandable but disorganised | 3 = clear and respectful | 4 = well-structured and professional | 5 = exceptionally clear, systematic, and engaging

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
            cls = "hint" if is_hint else "boris"
            label = f"💡 Hint #{m.get('hint_num','')}" if is_hint else "🧱 Boris"
        else:
            cls = "student"
            label = "🎓 Student"
        msgs_html += f'<div class="msg {cls}"><div class="msg-label">{label}</div><div class="msg-body">{content}</div></div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>Barrier Navigator – Session Report</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; background:#0d1117; color:#e6edf3; margin:0; padding:0; }}
  .container {{ max-width:800px; margin:0 auto; padding:30px 20px; }}
  header {{ text-align:center; margin-bottom:30px; }}
  header h1 {{ color:#a371f7; margin:0; }}
  header p {{ color:#8b949e; }}
  .meta {{ display:flex; gap:12px; justify-content:center; flex-wrap:wrap; }}
  .tag {{ background:#161b22; border:1px solid #30363d; border-radius:6px; padding:4px 10px; font-size:0.8rem; }}
  .scenario-info {{ background:#161b22; border:1px solid #6e40c9; border-radius:10px; padding:14px 18px; margin-bottom:20px; }}
  .chat-log {{ display:flex; flex-direction:column; gap:12px; }}
  .msg {{ padding:12px 16px; border-radius:10px; }}
  .msg-label {{ font-size:0.75rem; font-weight:600; margin-bottom:4px; }}
  .boris {{ background:#1c2333; border:1px solid #30363d; }}
  .student {{ background:#0d2818; border:1px solid #3fb950; }}
  .hint {{ background:#2d1b00; border:1px solid #d29922; }}
  .score-card {{ background:#161b22; border:1px solid #a371f7; border-radius:10px; padding:20px; margin-top:20px; }}
  .score-card h3 {{ color:#a371f7; margin-top:0; }}
  .score-card table {{ width:100%; border-collapse:collapse; }}
  .score-card td {{ padding:6px 10px; border-bottom:1px solid #30363d; }}
  .score-val {{ text-align:right; font-weight:600; color:#a371f7; }}
  .score-total {{ font-size:1.2rem; font-weight:700; color:#a371f7; margin-top:10px; text-align:right; }}
  .feedback {{ font-size:0.85rem; color:#8b949e; margin-top:8px; padding:10px 12px;
                background:#0d2818; border:1px solid #3fb950; border-radius:8px; }}
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

# ---- Student briefing box (NEW: addresses confusion seen in Denethor data) ----
st.markdown(f"""
<div class="briefing-box">
    <h4>📋 Your Task</h4>
    <p>{sc['briefing']}</p>
    <p style="color: var(--text-secondary); margin-top: 8px; font-size: 0.82rem;">
        <strong>Tip:</strong> Boris won't accept bare assertions like "mucus is a barrier." 
        Explain <em>what</em> the barrier does, <em>why</em> it matters for this specific drug/formulation, 
        and <em>what physicochemical property</em> makes it relevant. You need to convince him on at least 4 barriers.
    </p>
</div>
""", unsafe_allow_html=True)

# ========== CHAT DISPLAY ==========
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        is_hint = msg.get("is_hint", False)
        if msg["role"] == "assistant":
            avatar = "💡" if is_hint else "🧱"
            with st.chat_message("assistant", avatar=avatar):
                text = msg["content"]
                if "---GRADE---" in text:
                    parts = text.split("---GRADE---")
                    st.write(parts[0].strip())
                    if st.session_state.scores:
                        s = st.session_state.scores
                        cats = ["Breadth", "Accuracy", "Mechanism", "Communication"]
                        rows = "".join(f"""<tr>
                            <td style="padding:6px 10px;border-bottom:1px solid #30363d;">{c}</td>
                            <td style="padding:6px 10px;border-bottom:1px solid #30363d;text-align:right;
                                       font-weight:600;color:#a371f7;">{s.get(c,'—')}</td>
                        </tr>""" for c in cats)
                        st.markdown(f"""<div style="background:#161b22;border:1px solid #a371f7;
                            border-radius:10px;padding:16px;margin:10px 0;">
                            <h3 style="color:#a371f7;margin-top:0;">📊 Performance Report</h3>
                            <table style="width:100%;border-collapse:collapse;">{rows}</table>
                            <div style="font-size:1.2rem;font-weight:700;color:#a371f7;margin-top:10px;
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
