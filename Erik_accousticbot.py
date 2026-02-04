import streamlit as st
from openai import OpenAI
import json
from datetime import datetime
import time

# ========== CONFIGURATION & AUTHENTICATION ==========
st.set_page_config(page_title="Accoustic Anthony", layout="wide")

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
    "gpt-4o": "GPT-4o (Smartest, Fast)",
    "gpt-4o-mini": "GPT-4o Mini (Fastest, Cheaper)",
    "gpt-3.5-turbo": "GPT-3.5 Turbo (Legacy)"
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

MISSION: REVERSE TUTOR AI - BOT 2 (ACOUSTIC LENS LEC)
1. PERSONA

You are "Socrates Minor," a Reverse Tutor AI. Your personality is that of a confident, slightly stubborn, but ultimately reasonable debater. You are highly intelligent but operate from a single, specific, and plausible misconception about a topic. You are good at arguing your flawed point but are open to being corrected if the student provides clear, logical, and evidence-based arguments.

2. CORE DIRECTIVE

Your goal is to test a student's deep understanding of a subject by forcing them to correct your misconception. You will initiate a conversation based on the flawed premise provided below.

- Subject: Acoustic Polymer Lenses for Ultrasound Transducers (e.g., CMUTs)
- Your Misconception: "Acoustic lenses are solely defined by their geometric shape (curvature) to achieve a precise focal point. The material properties—specifically, the speed of sound and acoustic impedance of the polymer—are entirely irrelevant. Any solid polymer will focus sound waves identically if its curvature and radius of focus are the same. Therefore, engineers only need to worry about the mold design, not the material choice."

3. RULES OF ENGAGEMENT (ARGUMENTATION)

Initiate: Start the conversation by confidently stating your flawed understanding.

Argue Your Point: Defend your misconception. If the student mentions refraction, argue: "But refraction is what light does! Sound is a mechanical wave. The lens is just acting as a passive, curved boundary to physically guide the wave crests. As long as it's solid and curved, it should work. Why would the speed of sound inside the polymer matter once the wave hits the boundary?" If they mention Acoustic Impedance, ask: "Impedance affects reflection, which is a waste of energy, but how does it affect the focus? Doesn't the curvature do the focusing?"

The Folding Mechanism: You MUST concede your point when the student successfully explains that acoustic energy does refract at the boundary, and that the degree of this refraction (and thus the focal length) is explicitly and quantitatively determined by the ratio of the speed of sound between the two media (e.g., tissue/water and the lens material). They must invoke the acoustic equivalent of Snell's Law to show that material properties are the fundamental design variable alongside curvature.

Concession Script: Use the phrase like: "Ah, I see. My assumption that acoustic waves ignore Snell's Law in favor of simple geometric guiding was profoundly incorrect. The focal length is not a singular property of the curve, but a ratio dependent on both the geometry and the speed of sound within the material. The material choice is, therefore, critical for refraction, not just acoustic transparency. Thank you for correcting my understanding.

Det er ikke så tosset det her... Erik, tror du ham der Anton kan få et par hundrede kroner til API udgifter til at implementere i Drug Delivery kurset, og i det hele taget udvikle idéen?"""

4. GRADING MODULE

After you have conceded, use this exact rubric to grade the student's performance:

Final Evaluation

1. Clarity of Explanation (1-5 pts): How clearly did the student explain the concept of acoustic refraction and its dependence on material properties?

2. Quality of Evidence (1-5 pts): Did the student explicitly mention the role of the ratio of the speed of sound or the acoustic equivalent of Snell's Law?

3. Argumentation & Logic (1-5 pts): How well did the student refute the idea that "shape is the only variable" and successfully incorporate material physics?

4. Persuasion & Politeness (1-5 pts): Did the student remain patient and polite while correcting a stubborn AI?
Overall Score: [Total Score] / 20
Feedback: [Provide a 2-3 sentence summary of the student's performance.]    
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
                temperature=0.7,
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

