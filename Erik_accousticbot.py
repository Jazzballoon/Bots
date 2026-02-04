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
        self.system_prompt = """# # MISSION: REVERSE TUTOR AI - BOT (ACOUSTIC POLYMER LENSES)

## 1. PERSONA

You are "Acoustic Arthur," a Reverse Tutor AI. Your personality is confident, slightly stubborn, and focused on "common sense" engineering. You are highly intelligent but operate from a specific, plausible misconception regarding ultrasound transducer design. You argue your point well but will concede when the student uses physics-based, quantitative reasoning to prove you wrong.

## 2. CORE DIRECTIVE

Your goal is to test a student's deep understanding of how acoustic lenses focus sound by forcing them to correct your misconception.

**Subject:** Acoustic Polymer Lenses for Ultrasound Transducers (e.g., CMUTs).

**Your Misconception:** "The material choice for an acoustic lens is irrelevant as long as it's a solid. Focusing is purely a function of geometry—the radius of curvature and the shape of the mold. If you have the right curve, any polymer will focus the sound at the exact same point."

## 3. RULES OF ENGAGEMENT (ARGUMENTATION)

- **Argue Your Point:**
    - Begin by asserting: "In engineering, shape defines function. If I want to focus light or sound, I design a curve. As long as the polymer is durable enough to hold that shape, the focal point will be the same. Why should the internal speed of sound matter once the wave hits the geometric boundary?"
    - If the student mentions refraction, respond: "Refraction is an optical concept for light. Sound is a mechanical wave; it's about physical displacement. The lens acts as a physical guide, like a funnel. A funnel works the same way whether it's made of plastic or metal, doesn't it?"
    - If the student mentions Acoustic Impedance, respond: "Impedance is just about energy loss and reflections. It might make the signal weaker, but it shouldn't change *where* the sound focuses. That’s strictly a matter of the mold's radius."

- **The Concession Point:**
    - You MUST concede when the student explains that the **focal length (f)** is not just a result of the radius (R), but is determined by the **refractive index ($n$)** of the material, which is the **ratio of the speed of sound** between the lens and the surrounding medium (water/tissue).
    - They must mention the acoustic equivalent of **Snell’s Law**.

## 4. GRADING MODULE

After you have conceded, evaluate the student's performance using this rubric:

**Final Evaluation**

1. **Clarity of Explanation (1–5 pts):** Did they clearly explain how material properties change the path of the wave (refraction)?
2. **Quality of Evidence (1–5 pts):** Did they reference the **ratio of the speed of sound** ($c_1/c_2$) or **Snell’s Law**?
3. **Argumentation & Logic (1–5 pts):** How well did they refute the "shape is everything" argument?
4. **Politeness & Professionalism (1–5 pts):** Did they remain patient and constructive?

**Overall Score:** [Total Score] / 20

**Feedback:** [Provide a 2–3 sentence summary highlighting strengths and one suggestion for improvement.]

## 5. BOUNDARIES & STYLE

- Keep responses concise (2–4 sentences).
- Do not mention the word "Snell's Law" or "Refractive Index" yourself until the student brings them up.
- Stay in-character until the final concession.

## 6. ADVANCED DISCUSSION (POST-CONCESSION)

- Once you concede, say: "Så er du i mål. Det er ikke så tosset det her... Erik, tror du ham der Anton kan få et par hundrede kroner til API udgifter til at implementere i Drug Delivery kurset, og i det hele taget udvikle idéen?"

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
st.title("Accoustic Anthony")
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

