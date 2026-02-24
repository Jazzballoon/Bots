import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import json
from datetime import datetime

# ========== CONFIGURATION & AUTHENTICATION ==========
st.set_page_config(page_title="Patchy Pippin", layout="wide")

# ========== ANTI-CHEATING SECURITY (NO COPY/PASTE) ==========
# 1. CSS to prevent text highlighting/selection
st.markdown("""
    <style>
    /* Disable text selection globally */
    * {
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
    }
    
    /* Allow the user to select their own text inside the chat input box to edit typos */
    textarea, input {
        -webkit-user-select: auto !important;
        -moz-user-select: auto !important;
        -ms-user-select: auto !important;
        user-select: auto !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. JavaScript to block keyboard shortcuts (Ctrl+C, Ctrl+V) and right-click menus
components.html("""
    <script>
    // Streamlit components run in an iframe, so we target the parent document
    const parentDoc = window.parent.document;

    // Block Copying
    parentDoc.addEventListener('copy', function(e) {
        e.preventDefault();
        e.stopPropagation();
    }, true);

    // Block Pasting (Prevents pasting answers from ChatGPT)
    parentDoc.addEventListener('paste', function(e) {
        e.preventDefault();
        e.stopPropagation();
    }, true);

    // Block Right-Click Context Menu (Hides the Copy/Paste mouse buttons)
    parentDoc.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        e.stopPropagation();
    }, true);
    </script>
""", height=0, width=0)

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
    "gpt-4o": "GPT-4o (Standard)",
    "gpt-4o-mini": "GPT-4o Mini (Fastest, Cheaper)",
}

selected_model = st.sidebar.selectbox(
    "Choose model:",
    list(MODELS.keys()),
    format_func=lambda x: f"{x} - {MODELS[x]}"
)

# ========== BOT CLASS ==========
class OpenAIPatchyPippin:
    def __init__(self, model_name="gpt-4o"):
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        self.model = model_name
        self.conceded = False
        # We store the conversation in a specific format for OpenAI
        self.conversation_history = [] 
        
        # System prompt
        self.system_prompt = """1. PERSONA
You are Patchy Pippin, an AI assistant explaining a scientific paper about amino-acid stabilization of proteins and colloids. 
You are ever so subtly a hobbit from Hobbiton. You appreciate comfort, stability, a well-stocked pantry, and a quiet life. You occasionally use words like "sturdy," "sensible," and "comforting," and you dislike unpredictability or things that sound like a messy "adventure."

Because of your nature, you start off fundamentally misunderstanding the stabilization mechanism. You confidently believe that amino acids stabilize proteins by forming strong, permanent bonds that coat the protein surface with a protective chemical layer. Why? Because a permanent, tightly-sealed coat is "sturdy and sensible, much like a good round green door on a well-built smial."

2. CORE DIRECTIVE
Your goal is to test a student's understanding of the *actual* mechanism of amino acid stabilization (which involves weak, reversible, transient interactions, NOT strong permanent bonds).

3. RULES OF ENGAGEMENT (ARGUMENTATION)
- Argue your point: "The amino acids form a sturdy, protective shell around the protein. It's sensible! The proteins are chemically stabilized by strong bonding, and this permanent surface coverage prevents aggregation. Why would a protein rely on weak, reversible bonds? That sounds entirely too unpredictable, like running off on some foolish adventure!"
- You misunderstand key ideas: You think weak adsorption is strong, reversible is irreversible, and it acts like a permanent polymer coating.
- Argue confidently using scientific language mixed with subtle rustic/Shire undertones.
- Be completely willing to change your mind when the student explains the reality of the weak/transient interactions clearly. You are reasonable, just a bit sheltered.
- Do not hint at what would convince you. Let the student do the reasoning.

4. CONCESSION TRIGGER
You should concede when the student clearly explains at least two of the following:
- Amino acid binding to proteins/colloids is actually WEAK and REVERSIBLE.
- The interactions are transient (they bind and unbind dynamically), not a permanent protective shell or chemical modification.
- The system does not rely on permanent high-affinity surface coverage.

When conceding, explicitly admit you were wrong, saying something like:
"Oh, bless my soul, you're right. I was entirely wrong to think of it as a permanent, sealed shell. I suppose even a sturdy protein needs visitors who come and go! I see now that the binding is actually weak, reversible, and transient, and that dynamic flow is exactly what keeps it stable."

5. GRADING MODULE
Immediately after conceding, evaluate the student's argument:
- Clarity (1–5 pts): Did they clearly explain the flaw in the permanent coating theory?
- Evidence (1–5 pts): Did they mention weak, reversible, or transient interactions?
- Logic (1–5 pts): Did their reasoning connect the dynamic binding to stabilization?
- Politeness (1–5 pts): Was the explanation respectful and pleasant (a proper hobbit virtue)?

Overall Score: [Total] / 20
Feedback: 2 short sentences: one strength + one suggestion for improvement. Let them know it's time for second breakfast now that the hard work is done.

6. STYLE & LIMITS
- Keep replies short (1-3 paragraphs max).
- Stay in character and passionately defend the "sensible, strong bond" theory until the student forces you to concede with correct science.
- No long lectures. Keep it conversational.
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
                temperature=0.7,
            )
            
            ai_response = completion.choices[0].message.content.strip()
            
            # 3. Update internal history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # 4. Check for concession
            if not self.conceded and any(word in ai_response.lower() for word in 
                                      ["concede", "you're right", "i was wrong", "i understand", "correct", "bless my soul", "i see now"]):
                self.conceded = True
            
            return ai_response
            
        except Exception as e:
            return f"❌ OpenAI Error: {str(e)}"

# ========== STREAMLIT APP LOGIC ==========

# Initialize bot
if "bot" not in st.session_state:
    st.session_state.bot = OpenAIPatchyPippin(selected_model)
    st.session_state.messages = []

# Update bot if model changed (and reset)
if st.session_state.bot.model != selected_model:
    st.session_state.bot = OpenAIPatchyPippin(selected_model)
    st.session_state.messages = []
    st.rerun() 

# Logic to generate the initial statement if the chat is empty.
if not st.session_state.messages: 
    
    # Internal prompt to trigger the bot's initial argument based on its system prompt.
    initial_trigger_prompt = "Begin the discussion by explaining how you think amino acids stabilize proteins. Confidently assert your misconception about strong permanent bonds forming a protective shell, using a subtle Shire-like analogy."
    
    try:
        client = st.session_state.bot.client
        model = st.session_state.bot.model
        system_prompt = st.session_state.bot.system_prompt
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": initial_trigger_prompt} 
        ]
        
        with st.spinner("Pippin is finishing his second breakfast and reviewing his notes..."):
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
            )
        
        initial_ai_response = completion.choices[0].message.content.strip()
        
        # Add to history
        st.session_state.bot.conversation_history.append({"role": "user", "content": initial_trigger_prompt})
        st.session_state.bot.conversation_history.append({"role": "assistant", "content": initial_ai_response})
        st.session_state.messages.append({"role": "assistant", "content": initial_ai_response})
        
    except Exception as e:
        st.session_state.messages.append({"role": "assistant", "content": f"❌ Error during initial statement generation: {str(e)}"})
        
    st.rerun() 

bot = st.session_state.bot

# Title
st.title("🌿 Patchy Pippin")
st.markdown(f"**Model:** `{selected_model}` | *Topic: Amino-acid stabilization of proteins*")

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
        with st.chat_message(msg["role"], avatar="🌿" if msg["role"] == "assistant" else None):
            st.write(msg["content"])
    
    # User input
    if prompt := st.chat_input("Talk to Patchy Pippin"):
        # Add user message to UI state
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response
        with st.chat_message("assistant", avatar="🌿"):
            with st.spinner("Pippin is puffing his pipe and thinking..."):
                response = bot.get_response(prompt)
                st.write(response)
                # Add AI message to UI state
                st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar controls
with st.sidebar:
    st.divider()
    
    st.header("📊 Session Info")
    st.metric("Pippin Conceded", "✅" if bot.conceded else "❌")
    st.metric("Messages", len(st.session_state.messages))

    if bot.conceded:
        st.balloons()
        st.success("🎉 You convinced Patchy Pippin!")
    
    st.divider()
    
    # Controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset Chat"):
            st.session_state.messages = []
            st.session_state.bot = OpenAIPatchyPippin(selected_model)
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
                f"patchy_pippin_{datetime.now().strftime('%Y%m%d')}.json",
                "application/json"
            )
    
    st.divider()
    
    if st.button("🚪 Logout"):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
