import streamlit as st
import sys
sys.path.insert(0, ".")

st.set_page_config(page_title="⬡ Butler AI", page_icon="🤖", layout="wide")

st.markdown("""
<style>
.stApp{background:#06090d;color:#b8ccb8}
section[data-testid="stSidebar"]{background:#080c12;border-right:1px solid #1a2a1a}
.stTextInput>div>div>input,.stChatInput textarea{background:#0d1117;color:#c8dcc8;border:1px solid #1e3a1e}
.stButton>button{background:#0a2010;color:#00ff88;border:1px solid #00ff8850;border-radius:8px}
.stButton>button:hover{background:#143020}
h1,h2,h3{color:#00ff88!important}
.stSelectbox>div>div{background:#0d1117;color:#b8ccb8}
div[data-testid="stChatMessage"]{background:#0a0f0a;border:1px solid #1a2a1a;border-radius:8px;margin:4px 0}
code{background:#0a2010!important;color:#00ff88!important}
pre{background:#050a08!important;border:1px solid #1e3a1e!important}
</style>
""", unsafe_allow_html=True)

# ── Auth ──────────────────────────────────────────────────────────────────
import config
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("## 🔐 Butler AI")
        st.caption("Private — Only Your Commands")
        st.divider()
        pw = st.text_input("Password:", type="password", placeholder="Enter your secret password")
        if st.button("Unlock →", use_container_width=True):
            if pw == config.MY_PASSWORD:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Wrong password.")
        st.caption("🔒 AES-256 Encrypted · Private · Personal")
    st.stop()

# ── Lazy import after auth ────────────────────────────────────────────────
from orchestrator import run
from vector_store import recall_memory, save_feedback

# ── Session state ─────────────────────────────────────────────────────────
if "messages"      not in st.session_state: st.session_state.messages      = []
if "last_response" not in st.session_state: st.session_state.last_response = ""
if "rated"         not in st.session_state: st.session_state.rated         = False

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⬡ Butler AI")
    st.caption("Private Intelligence System")
    st.divider()

    mode = st.selectbox("Mode:", [
        "💬 General Chat",
        "🎓 Teaching Mode",
        "🔍 Deep Research",
        "👤 Social OSINT",
        "🧠 Analysis"
    ])

    st.divider()
    st.markdown("**⚡ Quick Topics:**")
    quick = [
        "Teach me SQL Injection",
        "Explain Neural Networks",
        "What is a firewall?",
        "How does encryption work?",
        "Teach me Nmap scanning",
        "What is machine learning?",
        "Explain Python decorators",
        "How does TCP/IP work?",
    ]
    for q in quick:
        if st.button(q, key=q, use_container_width=True):
            st.session_state.quick = q

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.session_state.last_response = ""
            st.session_state.rated = False
            st.rerun()
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.auth = False
            st.rerun()

    st.divider()
    st.caption("🔐 End-to-end encrypted")
    st.caption("🤖 Gemini + Llama ensemble")
    st.caption("🌐 Live web search")
    st.caption("🧠 Encrypted cloud memory")

# ── Main area ─────────────────────────────────────────────────────────────
st.markdown("# ⬡ Butler AI")
st.caption(f"{mode} · Encrypted · Self-Learning")
st.divider()

# Mode prefixes
MODE_PREFIX = {
    "🎓 Teaching Mode":  "Teach me step by step with examples and practical commands: ",
    "🔍 Deep Research":  "Research deeply and give detailed information about: ",
    "👤 Social OSINT":   "Search public social accounts and information for: ",
    "🧠 Analysis":       "Analyze deeply and give insights about: ",
    "💬 General Chat":   "",
}

# Display chat history
for msg in st.session_state.messages:
    icon = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=icon):
        st.markdown(msg["content"])

# Handle quick topic
if "quick" in st.session_state:
    prompt = st.session_state.pop("quick")
    full   = MODE_PREFIX.get(mode, "") + prompt
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("⬡ Thinking..."):
            response = run(full)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.last_response = response
    st.session_state.rated = False
    st.rerun()

# Chat input
prompt = st.chat_input("Give me a command...")
if prompt:
    full = MODE_PREFIX.get(mode, "") + prompt
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("⬡ Searching → Analyzing → Synthesizing..."):
            response = run(full)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.last_response = response
    st.session_state.rated = False

# Rating system
if st.session_state.last_response and not st.session_state.rated:
    st.divider()
    st.caption("Was this helpful? Rate it so I can learn:")
    c1, c2, c3, c4, c5 = st.columns(5)
    for i, (col, label) in enumerate(zip([c1,c2,c3,c4,c5], ["❌ Bad","😕 Poor","😐 OK","😊 Good","🌟 Perfect"]), 1):
        if col.button(label, key=f"r{i}"):
            save_feedback(st.session_state.last_response, i)
            st.session_state.rated = True
            msg = "✅ Saved as success pattern!" if i >= 4 else "📝 Saved as correction note — I'll improve!"
            st.success(msg)
            st.rerun()
