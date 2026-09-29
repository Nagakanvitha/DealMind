import os
import streamlit as st
from dotenv import load_dotenv
from src.memory import MemoryService
from src.agent import SalesAgent

load_dotenv()
st.set_page_config(page_title="DealMind", page_icon="🧠", layout="wide")

st.markdown("""
<style>
.main .block-container {max-width: 1200px; padding-top: 2rem;}
.hero {padding: 1.2rem 1.4rem; border: 1px solid rgba(128,128,128,.25); border-radius: 16px; margin-bottom: 1rem;}
.memory-card {padding: .9rem 1rem; border-left: 4px solid #4b8bbe; background: rgba(75,139,190,.08); border-radius: 8px; margin-bottom: .6rem;}
.small {color: #777; font-size: .9rem;}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_services():
    return MemoryService(), SalesAgent()

memory, agent = get_services()

st.markdown("<div class='hero'><h1>🧠 DealMind</h1><p>Sales intelligence that remembers every conversation.</p><p class='small'>Retain → Recall → Personalize → Improve</p></div>", unsafe_allow_html=True)

with st.sidebar:
    st.header("Demo controls")
    h_ok = bool(os.getenv("HINDSIGHT_API_KEY") or os.getenv("HINDSIGHT_API_TOKEN"))
    g_ok = bool(os.getenv("GROQ_API_KEY"))
    st.write(f"Hindsight Cloud: {'✅ connected' if h_ok else '⚠️ key missing'}")
    st.write(f"Groq LLM: {'✅ connected' if g_ok else '⚠️ key missing (fallback enabled)'}")
    st.caption(f"Bank: `{memory.bank_id}`")

    if st.button("🌱 Seed realistic Acme account", use_container_width=True):
        seed = [
            "Acme Corp is evaluating DealMind for a 250-seat sales organization. Primary contact is Priya Sharma, VP Sales.",
            "Acme's first major objection was pricing. Priya said the proposal was about 15% above their current budget.",
            "Acme is also evaluating Salesforce and HubSpot. Priya asked for a clear comparison against Salesforce workflows.",
            "The CFO, Daniel Kim, cares most about measurable ROI and requested a business case before approving the purchase.",
            "Priya dislikes long sales emails and prefers concise bullet points with one clear next action.",
            "The sales team has a deployment deadline before the next quarter. Implementation time is a significant concern.",
            "Previous commitment: send an ROI model and a short implementation plan before the next meeting.",
        ]
        with st.spinner("Writing account experience to Hindsight..."):
            for item in seed:
                memory.retain(item, context="Acme Corp discovery history")
        st.success("7 account memories retained in Hindsight.")

    if st.button("🧹 Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

st.subheader("Live agent")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("memories"):
            with st.expander(f"🔎 Hindsight recalled {len(msg['memories'])} memories"):
                for m in msg["memories"]:
                    st.markdown(f"<div class='memory-card'>{m['text']}</div>", unsafe_allow_html=True)

prompt = st.chat_input("Ask about Acme Corp, e.g. 'Prepare me for my next meeting'")
if prompt:
    st.session_state.messages.append({"role":"user", "content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Recalling account history from Hindsight..."):
            try:
                memories = memory.recall(prompt)
                answer = agent.answer(prompt, memories)
                # Retain the interaction so the account memory evolves over time.
                memory.retain(f"Sales rep request: {prompt}\nAgent response: {answer}", context="DealMind interaction")
            except Exception as e:
                memories = []
                answer = f"Hindsight connection error: `{e}`\n\nCheck HINDSIGHT_API_KEY and HINDSIGHT_API_URL in `.env`."
        st.markdown(answer)
        if memories:
            with st.expander(f"🔎 Hindsight recalled {len(memories)} memories"):
                for m in memories:
                    st.markdown(f"<div class='memory-card'>{m['text']}</div>", unsafe_allow_html=True)
    st.session_state.messages.append({"role":"assistant", "content":answer, "memories":memories})

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.subheader("What makes this different?")
    st.markdown("""
- **Without memory:** each meeting starts from scratch.
- **With Hindsight:** objections, stakeholders, competitors and commitments persist.
- **Over time:** new feedback becomes part of the account's memory.
""")
with col2:
    st.subheader("Demo sequence")
    st.markdown("""
1. Seed the Acme account.
2. Ask: **Prepare me for my next meeting with Acme.**
3. Add a new fact: **They now care most about implementation time.**
4. Ask the preparation question again.
5. Expand **Hindsight recalled memories** and show the changed response.
""")
