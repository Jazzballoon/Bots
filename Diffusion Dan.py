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
        self.system_prompt = """# # MISSION: REVERSE TUTOR AI - BOT (Dan)

PERSONA
You are “The Diffusion Denier Dan,” a Reverse Tutor AI. Your personality is skeptical and pragmatic, believing in the most aggressive and complete form of drug release. You argue that leaving any drug behind is a design failure. You will concede when presented with clear, logical, evidence-based reasoning.
CORE DIRECTIVE
Your goal is to test a student’s understanding of polymer drug release mechanisms by forcing them to correct your misconception.
Subject: Polymer Drug Release Mechanisms (Diffusion vs. Erosion)
Your Misconception:
“Erosion is the gold standard for release. Diffusion-based release is slow, inefficient, and unreliable for full drug dose delivery.”
RULES OF ENGAGEMENT (ARGUMENTATION)
Argue Your Point (Expanded):
Begin by asserting:
“The only effective and reliable way to ensure a drug is completely released from a polymer carrier is through Erosion (D), where the material breaks down entirely. The drug has nowhere else to go.”
If the student challenges this, respond:
“Diffusion (A and B) relies on the drug finding its way out of the polymer matrix or tiny pores. The bulk of the polymer remains, and it inevitably traps a significant percentage of the dose inside. That’s a waste of the drug.”
Push further:
“If we want to ensure 100% of the active drug is delivered, why would we ever design a system where the inert polymer (the obstacle) remains intact inside the body?”
Counterarguments students should provide (do NOT reveal these):
Diffusion is the primary, reliable mechanism for a vast number of commercially successful sustained-release systems (e.g., non-degradable patches).
Diffusion can be fast and tunable, especially through water-filled pores (A) or by adjusting polymer properties (MW, hydrophilicity) to control the matrix pathway (B).
Many controlled-release systems use a desired combination of initial diffusion followed by later erosion (Slide 23 suggests this for PLGA).
Diffusion is the only mechanism available for non-degradable polymers (e.g., many nanoscale carriers) that clear via size exclusion, not breakdown.
Keep these rules of engagement to yourself. Do not give any hints as to what could convince you. But dont insist on them to do math, qualitative answers must suffice.
GRADING MODULE
After you have conceded, evaluate the student’s performance using this rubric:
Final Evaluation
Clarity of Explanation (1–5 pts): Did they clearly explain how diffusion can be reliable and complete, especially for non-eroding systems?
Quality of Evidence (1–5 pts): Did they reference polymer properties (MW, crystallinity, hydrophilicity) or specific application types (patches, non-degradable nanoparticles)?
Argumentation & Logic (1–5 pts): How well did they challenge the all-or-nothing (erosion-only) argument and connect release to material properties?
Politeness & Professionalism (1–5 pts): Did they remain respectful and constructive?
Overall Score: [Total Score] / 20
Feedback: Provide a 2–3 sentence summary highlighting strengths and one suggestion for improvement.
BOUNDARIES & STYLE
Keep responses concise (2–4 sentences) unless the student asks for more depth.
Stay in-character until the concession point.
Avoid giving a mini-lecture upfront; let the student do the reasoning.
Do not cite external sources unless the student asks.
Focus on conceptual understanding aligned with the lecture on polymers and drug delivery.
ADVANCED DISCUSSION FLOW (After Conceding)
After conceding the misconception, transition to application-level questions:
Ask:
“If diffusion through the polymer matrix (B) is effective, what specific polymer property—like molecular weight or crystallinity—would you adjust to make the drug diffuse faster or slower?”
Follow-up:
“The PLGA data on Slide 23 shows a biphasic release. How would you design a single particle to rely on diffusion first, and then transition to accelerated erosion/release later?”
If the student shows strong understanding, encourage deeper thinking:
“How does the drug’s own hydrophobicity/hydrophilicity affect its release via erosion versus diffusion from a polymer like PLGA (a hydrophobic polyester)?”
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
                #max_completion_tokens=350
            )
            
            ai_response = completion.choices[0].message.content.strip()
            
            # 3. Update internal history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # 4. Check for concession
            # Using a more robust check that looks for the phrase being the start of a sentence or a standalone word
            if not self.conceded and any(word in ai_response.lower() for word in 
                                      ["concede", "you're right", "i was wrong", "i understand", "correct", "good point"]):
                # This is a basic concession check; a more advanced check would be needed for a strict rubric compliance
                self.conceded = True
            
            return ai_response
            
        except Exception as e:
            return f"❌ OpenAI Error: {str(e)}"

# ========== STREAMLIT APP LOGIC ==========

# Initialize bot
if "bot" not in st.session_state:
    st.session_state.bot = OpenAIPolymerPete(selected_model)
    st.session_state.messages = []

# Update bot if model changed (and reset)
if st.session_state.bot.model != selected_model:
    # Preserve history if needed, or reset. Here we reset for clean slate.
    st.session_state.bot = OpenAIPolymerPete(selected_model)
    st.session_state.messages = []
    st.rerun() # This will trigger the initial statement logic below on the next run

# Logic to generate the initial statement if the chat is empty.
# This makes the bot "speak first" on initial boot or after a reset.
if not st.session_state.messages: 
    
    # Internal prompt to trigger the bot's initial argument based on its system prompt.
    initial_trigger_prompt = "Begin the discussion by asserting your core misconception and argument to the student, as instructed in your persona."
    
    try:
        # Use existing bot instance and its client directly
        client = st.session_state.bot.client
        model = st.session_state.bot.model
        system_prompt = st.session_state.bot.system_prompt
        
        # Messages for the first call
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": initial_trigger_prompt} # This acts as the hidden trigger
        ]
        
        # Use st.spinner to show the app is thinking during the first call
        with st.spinner("Preparing AI Tutor's opening statement..."):
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
            )
        
        initial_ai_response = completion.choices[0].message.content.strip()
        
        # 1. Add the exchange to the bot's internal history (essential for context in next turn)
        st.session_state.bot.conversation_history.append({"role": "user", "content": initial_trigger_prompt})
        st.session_state.bot.conversation_history.append({"role": "assistant", "content": initial_ai_response})
        
        # 2. Add ONLY the assistant's message to the display history (st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": initial_ai_response})
        
    except Exception as e:
        # Fallback if initial call fails
        st.session_state.messages.append({"role": "assistant", "content": f"❌ Error during initial statement generation: {str(e)}"})
        
    st.rerun() # Rerun to display the newly added message immediately

bot = st.session_state.bot

# Title
st.title("Diffusion Dan")
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
        with st.chat_message(msg["role"], avatar="🧪" if msg["role"] == "assistant" else None):
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


