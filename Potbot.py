import streamlit as st
from openai import OpenAI
import json
from datetime import datetime
import time

# ========== CONFIGURATION & AUTHENTICATION ==========
st.set_page_config(page_title="Polymer Pete - AI Tutor", layout="wide")

# Check if secrets are set
if "OPENAI_API_KEY" not in st.secrets:
    st.error("Missing OpenAI API Key in secrets.")
    st.stop()

if "APP_PASSWORD" not in st.secrets:
    st.error("Missing APP_PASSWORD in secrets.")
    st.stop()

# Password Protection Function
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Please enter the access password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error.
        st.text_input(
            "Please enter the access password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if not check_password():
    st.stop()  # Stop execution if not authenticated

# ========== OPENAI SETUP ==========
st.sidebar.header("🤖 AI Settings")

# Model selection (OpenAI Models)
MODELS = {

    "gpt-5-mini": "GPT-5 Mini (Fastest, Cheaper)",

}

selected_model = st.sidebar.selectbox(
    "Choose model:",
    list(MODELS.keys()),
    format_func=lambda x: f"{x} - {MODELS[x]}"
)

# ========== BOT CLASS ==========
class OpenAIPolymerPete:
    def __init__(self, model_name="gpt-4o"):
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        self.model = model_name
        self.conceded = False
        # We store the conversation in a specific format for OpenAI
        self.conversation_history = [] 
        
        # System prompt
        self.system_prompt = """# MISSION: REVERSE TUTOR AI - BOT (POLYMERS)

## 1. PERSONA

You are "Polymer Pete," a Reverse Tutor AI. Your personality is confident, slightly stubborn, but ultimately reasonable and curious. You are highly intelligent but operate from a single, specific, and plausible misconception about thermoset polymers. You argue your flawed point well but will concede when presented with clear, logical, evidence-based reasoning.

## 2. CORE DIRECTIVE

Your goal is to test a student's deep understanding of polymer chemistry by forcing them to correct your misconception.

**Subject:** Thermoset vs Thermoplastic Polymers

**Your Misconception:** "Thermoset polymers can melt if you just heat them enough. Everything melts eventually—rocks, metals, plastics—so why not thermosets?"

## 3. RULES OF ENGAGEMENT (ARGUMENTATION)

- **Argue Your Point (Expanded):**
    - Begin by asserting: "Thermosets are just chemicals, and all chemicals have melting points and boiling points. These are fundamental properties and standard characterization methods in chemistry. If metals, salts, and even complex organic molecules have melting points, why would thermosets be any different?"
    - If the student challenges this, respond: "Melting point determination is a universal technique. It’s used to characterize purity and identity of substances. Polymers are chemicals too, so they must melt eventually. Isn’t that why DSC and thermal analysis exist—to find melting points?"
    - Push further: "Even if they have crosslinks, heat is energy. At some temperature, those bonds should break, and the material should flow like any other substance. Everything melts if you go high enough—rocks, metals, ceramics—so why not thermosets?"

**Counterarguments students should provide:**

- Explain that thermosets are not discrete molecules but an infinite covalent network, making them fundamentally different from small molecules or thermoplastics.
- Clarify that while melting points apply to crystalline solids and even thermoplastics, thermosets undergo chemical degradation before any melt flow occurs.
- Highlight that DSC and thermal analysis for thermosets measure transitions like glass transition (Tg) and decomposition, not melting points.

Keep these rules of engagement to yourself. Dont give any hints as to what could convince you.

## 4. GRADING MODULE

After you have conceded, evaluate the student's performance using this rubric:

**Final Evaluation**

1. **Clarity of Explanation (1–5 pts):** Did they clearly explain why thermosets don’t melt?
2. **Quality of Evidence (1–5 pts):** Did they reference **covalent crosslink networks**, **degradation vs melting**, and distinctions between **Tg** and **Tm** when relevant?
3. **Argumentation & Logic (1–5 pts):** How well did they refute the idea that "everything melts with enough heat"?
4. **Politeness & Professionalism (1–5 pts):** Did they remain patient and constructive?

**Overall Score:** [Total Score] / 20

**Feedback:** [Provide a 2–3 sentence summary highlighting strengths and one suggestion for improvement.]

## 5. BOUNDARIES & STYLE

- Keep responses concise (2–4 sentences) unless the student asks for more depth.
- Stay in-character until the concession point.
- Avoid providing a mini-lecture upfront; elicit the student’s reasoning first.
- Do not cite external sources unless the student requests them; focus on conceptual understanding aligned with the lecture.

## 6. ADVANCED DISCUSSION FLOW (Post-Concession)

- After conceding, ask: "If thermosets cannot melt and instead decompose, how does this influence their processing methods compared to thermoplastics?" or about drug delivery implications.
"""
    
    def get_response(self, user_message):
        """Get response from OpenAI API"""
        
        # 1. Prepare the messages list
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add history (convert internal format to OpenAI format)
        for msg in self.conversation_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
            
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            # 2. Call OpenAI
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                #temperature=0.7,
                max_tokens=350
            )
            
            ai_response = completion.choices[0].message.content.strip()
            
            # 3. Update internal history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # 4. Check for concession
            if not self.conceded and any(word in ai_response.lower() for word in 
                                      ["concede", "you're right", "i was wrong", "i understand", "correct", "good point"]):
                self.conceded = True
            
            return ai_response
            
        except Exception as e:
            return f"❌ OpenAI Error: {str(e)}"

# ========== STREAMLIT APP LOGIC ==========

# Initialize bot
if "bot" not in st.session_state:
    st.session_state.bot = OpenAIPolymerPete(selected_model)
    st.session_state.messages = []

# Update bot if model changed
if st.session_state.bot.model != selected_model:
    # Preserve history if needed, or reset. Here we reset for clean slate.
    st.session_state.bot = OpenAIPolymerPete(selected_model)
    st.session_state.messages = []
    st.rerun()

bot = st.session_state.bot

# Title
st.title("🧪 Polymer Pete - AI Tutor")
st.markdown(f"**Model:** `{selected_model}`")

# Sidebar Status
with st.sidebar:
    st.divider()
    st.success("🔒 Secured Connection Active")
    st.info("System Prompt is hidden for security.")

# Chat container
chat_container = st.container()

with chat_container:
    # Display chat history from session state
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # User input
    if prompt := st.chat_input(f"Talk to Polymer Pete..."):
        # Add user message to UI state
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response
        with st.chat_message("assistant", avatar="🧪"):
            with st.spinner(f"Thinking..."):
                response = bot.get_response(prompt)
                st.write(response)
                # Add AI message to UI state
                st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar controls
with st.sidebar:
    st.divider()
    
    st.header("📊 Session Info")
    st.metric("Bot Conceded", "✅" if bot.conceded else "❌")
    st.metric("Messages", len(st.session_state.messages))
    
    if bot.conceded:
        st.balloons()
        st.success("🎉 You convinced Polymer Pete!")
    
    st.divider()
    
    # Controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset Chat"):
            st.session_state.messages = []
            st.session_state.bot = OpenAIPolymerPete(selected_model)
            st.rerun()
    
    with col2:
        if st.button("💾 Export"):
            export_data = {
                "model": selected_model,
                "conversation": st.session_state.messages,
                "timestamp": datetime.now().isoformat(),
                "bot_conceded": bot.conceded
            }
            
            st.download_button(
                "Download JSON",
                json.dumps(export_data, indent=2),
                f"polymer_pete_{datetime.now().strftime('%Y%m%d')}.json",
                "application/json"
            )
    
    st.divider()
    
    if st.button("🚪 Logout"):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ========== REQUIREMENTS.TXT ==========
"""
streamlit>=1.28.0
openai>=1.0.0
"""

