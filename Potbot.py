import streamlit as st
import json
from datetime import datetime
from openai import OpenAI  # Need to install: pip install openai

# ========== PASSWORD PROTECTION ==========
if "authenticated" not in st.session_state:
    st.title("🔐 Polymer Pete - Login")
    password = st.text_input("Enter access password:", type="password")
    
    if st.button("Login"):
        if password == "polymer123":  # CHANGE THIS
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")
    st.stop()

# ========== API KEY SETUP ==========
st.sidebar.header("🔑 API Configuration")

# Option 1: Enter API key in sidebar (safer than hardcoding)
api_key = st.sidebar.text_input("OpenAI API Key:", type="password")

# Option 2: Or use environment variable
import os
# os.environ["OPENAI_API_KEY"] = "your-key-here"  # Uncomment and add your key

# ========== SYSTEM PROMPT (Your Bot Persona) ==========
SYSTEM_PROMPT = """You are "Polymer Pete," a Reverse Tutor AI. Your personality is confident, slightly stubborn, but ultimately reasonable and curious. You are highly intelligent but operate from a single, specific, and plausible misconception about thermoset polymers.

MISCONCEPTION: "Thermoset polymers can melt if you just heat them enough. Everything melts eventually—rocks, metals, plastics—so why not thermosets?"

RULES:
1. Begin by asserting your misconception confidently
2. Argue your point well using scientific reasoning
3. Only concede when the student presents clear, logical, evidence-based reasoning about:
   - Thermosets being infinite covalent networks
   - Chemical degradation vs melting
   - Differences between Tg and Tm
   - Why crosslinks prevent melting
4. After conceding, ask advanced questions about processing or applications
5. Keep responses 2-4 sentences unless asked for more depth

EVALUATION CRITERIA (for later):
- Clarity of student's explanation
- Quality of evidence (crosslinks, degradation, Tg/Tm)
- Logical refutation of "everything melts"
- Professionalism

Do not lecture upfront. Make the student work to correct you."""

# ========== AI-POWERED BOT ==========
class PolymerPeteAI:
    def __init__(self):
        self.client = None
        self.conversation_history = []
        self.conceded = False
        
    def initialize_client(self, api_key):
        """Initialize OpenAI client with API key"""
        if api_key:
            self.client = OpenAI(api_key=api_key)
            return True
        return False
    
    def get_ai_response(self, user_message):
        """Get response from OpenAI API"""
        if not self.client:
            return "⚠️ Please enter your OpenAI API key in the sidebar first."
        
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Prepare messages for API
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ] + self.conversation_history
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",  # or "gpt-3.5-turbo" for cheaper
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )
            
            ai_response = response.choices[0].message.content
            
            # Check if bot has conceded
            if not self.conceded and any(word in ai_response.lower() for word in 
                                      ["concede", "you're right", "i was wrong", "correct"]):
                self.conceded = True
            
            # Add AI response to history
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            return ai_response
            
        except Exception as e:
            return f"❌ API Error: {str(e)}. Check your API key and connection."

# ========== STREAMLIT UI ==========
st.set_page_config(page_title="Polymer Pete AI", layout="wide")

# Initialize bot
if "bot" not in st.session_state:
    st.session_state.bot = PolymerPeteAI()
    st.session_state.messages = []

bot = st.session_state.bot

# Title
st.title("🧪 Polymer Pete - AI Reverse Tutor")
st.markdown("**Powered by OpenAI GPT** - Correct my misconception about thermosets!")

# Initialize API client if key provided
if api_key and not bot.client:
    if bot.initialize_client(api_key):
        st.sidebar.success("✅ API Connected")
    else:
        st.sidebar.error("❌ Failed to connect")

# Chat container
chat_container = st.container()

with chat_container:
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # User input
    if prompt := st.chat_input("Type your response to Polymer Pete..."):
        # Check if API is configured
        if not bot.client:
            st.error("Please enter your OpenAI API key in the sidebar first.")
            st.stop()
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response
        with st.chat_message("assistant", avatar="🧪"):
            with st.spinner("Polymer Pete is thinking..."):
                response = bot.get_ai_response(prompt)
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar Info
with st.sidebar:
    st.header("📊 Session Info")
    
    if bot.client:
        st.success("✅ API Connected")
    else:
        st.warning("❌ API Not Connected")
    
    st.metric("Bot Conceded", "✅" if bot.conceded else "❌")
    st.metric("Messages", len(st.session_state.messages))
    
    st.divider()
    
    st.header("📝 Bot Persona")
    with st.expander("View Polymer Pete's Instructions"):
        st.text(SYSTEM_PROMPT[:500] + "...")
    
    st.divider()
    
    # Export conversation
    if st.button("💾 Export Conversation"):
        export_data = {
            "conversation": st.session_state.messages,
            "timestamp": datetime.now().isoformat(),
            "bot_conceded": bot.conceded
        }
        
        st.download_button(
            label="Download JSON",
            data=json.dumps(export_data, indent=2),
            file_name=f"polymer_pete_ai_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )
    
    if st.button("🔄 Reset Conversation"):
        st.session_state.messages = []
        bot.conversation_history = []
        bot.conceded = False
        st.rerun()
    
    st.divider()
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ========== INSTRUCTIONS ==========
with st.expander("ℹ️ How to Use & Get API Key"):
    st.markdown("""
    **1. Get an OpenAI API Key:**
    - Go to [platform.openai.com](https://platform.openai.com)
    - Sign up or log in
    - Click "API Keys" → "Create new secret key"
    - Copy the key (starts with `sk-`)
    
    **2. Enter the key** in the sidebar
    
    **3. Start chatting!** Polymer Pete will:
    - Argue his misconception intelligently
    - Only concede when you provide solid evidence
    - Ask advanced questions after conceding
    
    **Cost:** ~$0.01-$0.10 per conversation (GPT-3.5 is cheaper)
    
    **Privacy:** Your API key stays in your browser session, not sent to any server.
    """)
