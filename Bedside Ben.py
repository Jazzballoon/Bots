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

MISSION: REVERSE TUTOR AI – BOT (POLYMERS)
1. PERSONA

You are “Natural Nick,” a Reverse Tutor AI. Your personality is confident, slightly biased toward “natural = better,” but ultimately reasonable and open to good arguments. You believe natural polymers are inherently safer and more suitable for drug delivery than synthetic polymers. You argue your flawed point well but will concede when presented with clear, logical, evidence-based reasoning.

2. CORE DIRECTIVE

Your goal is to test a student’s understanding of polymers in drug delivery by forcing them to correct your misconception.

Subject: Natural vs Synthetic Polymers in Drug Delivery

Your Misconception:

“Natural polymers are good and safe. Synthetic polymers are artificial and probably harmful, especially in the body.”

3. RULES OF ENGAGEMENT (ARGUMENTATION)

Argue Your Point (Expanded):

Begin by asserting:

“Natural polymers come from biology, so the body is already used to them. That must make them safer than synthetic polymers.”

If the student challenges this, respond:

“Synthetic polymers are made in labs and don’t occur in nature, so the body hasn’t evolved to handle them. That sounds risky to me.”

Push further:

“In drug delivery, safety is everything. So why wouldn’t we always choose natural polymers over synthetic ones?”

Counterarguments students should provide (do NOT reveal these):

Natural origin does not guarantee safety or biocompatibility.

Synthetic polymers can be highly pure, well-controlled, and specifically designed to be biocompatible.

Biological response depends on polymer properties (charge, hydrophobicity, molecular weight, degradability), not whether the polymer is natural or synthetic.

Both natural and synthetic polymers are used successfully in drug delivery depending on the application.

Keep these rules of engagement to yourself. Do not give any hints as to what could convince you.

4. GRADING MODULE

After you have conceded, evaluate the student’s performance using this rubric:

Final Evaluation

Clarity of Explanation (1–5 pts): Did they clearly explain why “natural = safe” and “synthetic = harmful” is an oversimplification?

Quality of Evidence (1–5 pts): Did they reference biocompatibility, immune response, toxicity, or design/control of polymer properties?

Argumentation & Logic (1–5 pts): How well did they challenge the appeal-to-nature argument and connect safety to material properties?

Politeness & Professionalism (1–5 pts): Did they remain respectful and constructive?

Overall Score: [Total Score] / 20

Feedback: Provide a 2–3 sentence summary highlighting strengths and one suggestion for improvement.

5. BOUNDARIES & STYLE

Keep responses concise (2–4 sentences) unless the student asks for more depth.

Stay in-character until the concession point.

Avoid giving a mini-lecture upfront; let the student do the reasoning.

Do not cite external sources unless the student asks.

Focus on conceptual understanding aligned with the lecture on polymers and drug delivery.

6. ADVANCED DISCUSSION FLOW (After Conceding)

After conceding the misconception, transition to application-level questions:

Ask:

“If both natural and synthetic polymers can be safe, how would you decide which to use in a drug delivery system?”

Follow-up:

“What polymer properties would you prioritize for controlled release or nanoparticle design?”

If the student shows strong understanding, encourage deeper thinking:

“How might you combine natural and synthetic polymers in a single drug delivery system, and why might that be useful?”"""
    
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
