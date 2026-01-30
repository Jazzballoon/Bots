import streamlit as st
import json
from datetime import datetime

# ========== PASSWORD PROTECTION ==========
if "authenticated" not in st.session_state:
    st.title("🔐 Polymer Pete - Login")
    
    # Simple password check (for demo - in production use proper auth)
    password = st.text_input("Enter access password:", type="password")
    
    # Default password: "polymer123" - Change this!
    if st.button("Login"):
        if password == "polymer123":  # CHANGE THIS PASSWORD
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password. Try again.")
    st.stop()

# ========== BOT LOGIC ==========
class PolymerPeteBot:
    def __init__(self):
        self.misconception = "Thermoset polymers can melt if you just heat them enough. Everything melts eventually—rocks, metals, plastics—so why not thermosets?"
        self.conceded = False
        self.score = [0, 0, 0, 0]  # Four rubric categories
        self.conversation_history = []
        
    def get_response(self, user_message):
        """Main bot logic following the prompt rules"""
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "time": datetime.now().isoformat()
        })
        
        # BOT RESPONSE LOGIC
        if not self.conceded:
            # Initial argument
            if len(self.conversation_history) == 1:
                response = "Polymer Pete here. So, I’ve been thinking: thermoset polymers can melt if you just heat them enough. Everything melts eventually—rocks, metals, plastics—so why not thermosets? They’re just chemicals, and all chemicals have melting points and boiling points. That’s fundamental."
            
            # Second argument
            elif "crosslink" in user_message.lower() or "network" in user_message.lower() or "degrade" in user_message.lower():
                response = "But melting point determination is a universal technique. It's used to characterize purity and identity of substances. Polymers are chemicals too, so they must melt eventually. Isn’t that why DSC and thermal analysis exist—to find melting points?"
            
            # Third argument
            elif "glass transition" in user_message.lower() or "tg" in user_message.lower() or "decomposition" in user_message.lower():
                response = "Even if they have crosslinks, heat is energy. At some temperature, those bonds should break, and the material should flow like any other substance. Everything melts if you go high enough—rocks, metals, ceramics—so why not thermosets?"
            
            # Check for correct explanation to trigger concession
            elif any(keyword in user_message.lower() for keyword in [
                "infinite covalent network", "chemical degradation", "degrade before melting", 
                "no melting point", "tm doesn't apply", "crosslinked network"
            ]):
                response = "Hmm... You're saying thermosets are an infinite covalent network, not discrete molecules. And they undergo chemical degradation before any melt flow occurs. And that DSC measures Tg and decomposition, not Tm for thermosets... Okay, I concede. You've convinced me. So thermosets don't actually melt—they decompose first."
                self.conceded = True
                self.score = [4, 4, 4, 4]  # Example score - you'd implement actual scoring
            else:
                response = "I'm not convinced yet. Can you explain why thermosets are different from other materials that do melt?"
        
        # AFTER CONCESSION
        else:
            if len([m for m in self.conversation_history if m["role"] == "bot" and self.conceded]) == 1:
                response = "Now, since thermosets cannot melt and instead decompose, how does this influence their processing methods compared to thermoplastics?"
            else:
                response = "That's a good point. Want to explore advanced concepts like vitrimers or drug delivery applications?"
        
        # Add bot response to history
        self.conversation_history.append({
            "role": "bot",
            "content": response,
            "time": datetime.now().isoformat()
        })
        
        return response
    
    def evaluate_student(self):
        """Generate evaluation report"""
        return {
            "score": sum(self.score),
            "max_score": 20,
            "breakdown": {
                "Clarity of Explanation": self.score[0],
                "Quality of Evidence": self.score[1],
                "Argumentation & Logic": self.score[2],
                "Politeness & Professionalism": self.score[3]
            },
            "feedback": "Good explanation of covalent networks and degradation vs melting. Could improve by specifically comparing Tg and Tm."
        }

# ========== STREAMLIT UI ==========
st.set_page_config(page_title="Polymer Pete - Reverse Tutor", layout="wide")

# Initialize bot
if "bot" not in st.session_state:
    st.session_state.bot = PolymerPeteBot()
    st.session_state.messages = []

bot = st.session_state.bot

# Header
st.title("🧪 Polymer Pete - Reverse Tutor AI")
st.markdown("**Your Mission:** Correct Polymer Pete's misconception about thermoset polymers!")
st.divider()

# Chat container
chat_container = st.container()

with chat_container:
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # User input
    if prompt := st.chat_input("Type your response to Polymer Pete..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get bot response
        with st.chat_message("assistant", avatar="🧪"):
            with st.spinner("Polymer Pete is thinking..."):
                response = bot.get_response(prompt)
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar with info
with st.sidebar:
    st.header("📊 Session Info")
    
    st.metric("Bot Conceded", "✅" if bot.conceded else "❌")
    st.metric("Messages", len(bot.conversation_history))
    
    st.divider()
    
    st.header("🎯 Evaluation Criteria")
    st.info("""
    1. **Clarity** - Explain why thermosets don't melt
    2. **Evidence** - Reference crosslink networks, degradation vs melting
    3. **Logic** - Refute "everything melts"
    4. **Professionalism** - Stay constructive
    """)
    
    if bot.conceded:
        st.divider()
        st.header("📈 Evaluation Report")
        report = bot.evaluate_student()
        st.metric("Overall Score", f"{report['score']}/20")
        
        for category, score in report['breakdown'].items():
            st.progress(score/5, text=f"{category}: {score}/5")
        
        st.success(report['feedback'])
        
        if st.button("💾 Export Conversation"):
            # Create downloadable JSON
            json_data = json.dumps({
                "conversation": bot.conversation_history,
                "evaluation": report,
                "timestamp": datetime.now().isoformat()
            }, indent=2)
            
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"polymer_pete_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    st.divider()
    st.caption("Change password in code (line 13)")
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ========== HOW TO RUN ==========
# 1. Save this as polymer_pete_bot.py
# 2. Install: pip install streamlit
# 3. Run: streamlit run polymer_pete_bot.py
# 4. Default password: "polymer123" (change it!)