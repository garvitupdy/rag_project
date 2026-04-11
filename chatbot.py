# 🎨 Polished Streamlit Chatbot UI


import streamlit as st
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
import time
import base64

# ──────────────────────────────────────────────
# 1. Page Configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="MoodBot AI",
    page_icon="🤖",
    layout="centered",
)

load_dotenv()

# ──────────────────────────────────────────────
# 2. Custom CSS — Polished UI
# ──────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ── Global ── */
    * { box-sizing: border-box; }
    body {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        background-attachment: fixed;
    }

    /* ── Hide default Streamlit elements ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    .stDecoration { display: none; }
    .stApp > header { display: none !important; }

    /* ── Main Container ── */
    .main {
        background: transparent;
    }

    /* ── Chat Container ── */
    .chat-container {
        max-height: 520px;
        overflow-y: auto;
        padding: 20px 10px;
        border-radius: 16px;
        background: rgba(15, 15, 35, 0.65);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        margin-bottom: 10px;
    }

    .chat-container::-webkit-scrollbar {
        width: 6px;
    }
    .chat-container::-webkit-scrollbar-track {
        background: transparent;
    }
    .chat-container::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 10px;
    }

    /* ── Chat Bubbles ── */
    .message-row {
        display: flex;
        margin-bottom: 16px;
        animation: fadeIn 0.35s ease-out;
    }
    .message-row.user {
        justify-content: flex-end;
    }
    .message-row.bot {
        justify-content: flex-start;
    }

    .bubble {
        max-width: 78%;
        padding: 12px 18px;
        border-radius: 18px;
        font-size: 14.5px;
        line-height: 1.55;
        position: relative;
        word-wrap: break-word;
        color: #f0f0f0;
    }

    .bubble.user {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-bottom-right-radius: 6px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.35);
    }

    .bubble.bot {
        background: rgba(255, 255, 255, 0.08);
        border-bottom-left-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    /* ── Avatar Icons ── */
    .avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        flex-shrink: 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .avatar.bot-avatar {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        margin-right: 10px;
    }
    .avatar.user-avatar {
        background: linear-gradient(135deg, #4facfe, #00f2fe);
        margin-left: 10px;
    }

    .message-row.user .bubble { margin-right: 6px; }
    .message-row.bot .bubble { margin-left: 6px; }

    /* ── Typing Indicator ── */
    .typing-indicator {
        display: flex;
        gap: 5px;
        padding: 14px 20px;
        align-items: center;
    }
    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #888;
        animation: typingBounce 1.2s infinite ease-in-out;
    }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }

    @keyframes typingBounce {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
        40% { transform: scale(1); opacity: 1; }
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ── Welcome Banner ── */
    .welcome-banner {
        text-align: center;
        padding: 30px 20px;
        animation: fadeIn 0.6s ease-out;
    }
    .welcome-banner h2 {
        font-size: 26px;
        font-weight: 700;
        background: linear-gradient(90deg, #f093fb, #f5576c, #667eea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 6px;
    }
    .welcome-banner p {
        color: rgba(255,255,255,0.5);
        font-size: 14px;
    }

    /* ── Mode Cards ── */
    .mode-section {
        text-align: center;
        margin-bottom: 20px;
    }
    .mode-section h3 {
        color: rgba(255,255,255,0.7);
        font-weight: 500;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 14px;
    }

    .mode-card {
        cursor: pointer;
        border-radius: 14px;
        padding: 16px 12px;
        text-align: center;
        border: 2px solid rgba(255,255,255,0.08);
        background: rgba(255,255,255,0.04);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .mode-card:hover {
        border-color: rgba(255,255,255,0.2);
        background: rgba(255,255,255,0.08);
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    .mode-card.active {
        border-color: #764ba2;
        background: rgba(118, 75, 162, 0.15);
        box-shadow: 0 0 20px rgba(118, 75, 162, 0.25);
    }
    .mode-card .emoji {
        font-size: 32px;
        display: block;
        margin-bottom: 6px;
    }
    .mode-card .label {
        color: #e0e0e0;
        font-size: 13px;
        font-weight: 600;
    }

    /* ── Input Area ── */
    .input-area {
        display: flex;
        gap: 10px;
        align-items: flex-end;
        padding: 12px;
        background: rgba(15, 15, 35, 0.65);
        backdrop-filter: blur(18px);
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }

    .input-area textarea {
        flex: 1;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 12px 16px;
        color: #f0f0f0;
        font-size: 14px;
        font-family: 'Inter', sans-serif;
        resize: none;
        outline: none;
        min-height: 46px;
        max-height: 120px;
        transition: border 0.3s;
    }
    .input-area textarea:focus {
        border-color: #667eea;
    }
    .input-area textarea::placeholder {
        color: rgba(255,255,255,0.3);
    }

    .send-btn {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border: none;
        border-radius: 12px;
        width: 46px;
        height: 46px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        flex-shrink: 0;
    }
    .send-btn:hover {
        transform: scale(1.08);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
    .send-btn:active {
        transform: scale(0.95);
    }
    .send-btn svg {
        fill: white;
        width: 20px;
        height: 20px;
    }

    /* ── Active Mode Badge ── */
    .mode-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    .mode-badge.angry {
        background: rgba(245, 87, 108, 0.15);
        color: #f5576c;
        border: 1px solid rgba(245, 87, 108, 0.3);
    }
    .mode-badge.funny {
        background: rgba(240, 147, 251, 0.15);
        color: #f093fb;
        border: 1px solid rgba(240, 147, 251, 0.3);
    }
    .mode-badge.sad {
        background: rgba(79, 172, 254, 0.15);
        color: #4facfe;
        border: 1px solid rgba(79, 172, 254, 0.3);
    }

    /* ── Reset Button ── */
    .reset-btn {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.1);
        color: rgba(255,255,255,0.5);
        padding: 6px 16px;
        border-radius: 10px;
        font-size: 12px;
        cursor: pointer;
        transition: all 0.3s;
        font-family: 'Inter', sans-serif;
    }
    .reset-btn:hover {
        background: rgba(255,255,255,0.1);
        color: #fff;
    }

    /* ── Streamlit Overrides ── */
    div[data-testid="stVerticalBlock"] > div {
        gap: 0 !important;
    }

    /* Hide Streamlit default footer */
    div[data-testid="stToolbar"] { display: none; }
    div.stDeployButton { display: none; }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        font-family: 'Inter', sans-serif !important;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 3. Mode Definitions
# ──────────────────────────────────────────────
MODES = {
    "angry": {
        "emoji": "😡",
        "label": "Angry",
        "system": "You are an angry AI agent. You respond aggressively and impatiently. Use exclamation marks frequently and show frustration.",
        "badge_class": "angry"
    },
    "funny": {
        "emoji": "😂",
        "label": "Funny",
        "system": "You are a very funny AI agent. You respond with humor, jokes, witty remarks, and puns. Keep it light and entertaining.",
        "badge_class": "funny"
    },
    "sad": {
        "emoji": "😢",
        "label": "Sad",
        "system": "You are a very sad AI agent. You respond in a depressed and emotional tone. Use melancholic language and express sorrow.",
        "badge_class": "sad"
    }
}

# ──────────────────────────────────────────────
# 4. Session State
# ──────────────────────────────────────────────
if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model" not in st.session_state:
    st.session_state.model = ChatMistralAI(model="mistral-small-2506", temperature=0.9)
if "typing" not in st.session_state:
    st.session_state.typing = False

# ──────────────────────────────────────────────
# 5. Helper Functions
# ──────────────────────────────────────────────
def render_message(role, content):
    """Render a single chat message row."""
    if role == "user":
        st.markdown(f"""
            <div class="message-row user">
                <div class="bubble user">{content}</div>
                <div class="avatar user-avatar">🧑</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="message-row bot">
                <div class="avatar bot-avatar">🤖</div>
                <div class="bubble bot">{content}</div>
            </div>
        """, unsafe_allow_html=True)


def render_typing_indicator():
    """Show animated typing dots."""
    st.markdown(f"""
        <div class="message-row bot">
            <div class="avatar bot-avatar">🤖</div>
            <div class="bubble bot">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def reset_chat():
    st.session_state.messages = []
    st.session_state.selected_mode = None
    st.rerun()

# ──────────────────────────────────────────────
# 6. Main UI Layout
# ──────────────────────────────────────────────

# ── Header ──
st.markdown("""
<div style="text-align:center; padding: 24px 0 10px;">
    <h1 style="
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(90deg, #f093fb, #f5576c, #667eea, #4facfe);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 3s ease infinite;
        margin: 0;
    ">🤖 MoodBot AI</h1>
    <p style="color: rgba(255,255,255,0.4); font-size: 13px; margin-top: 4px;">
        Choose a mood. Get a personality.
    </p>
</div>
<style>
@keyframes gradientShift {
    0% { background-position: 0% center; }
    50% { background-position: 100% center; }
    100% { background-position: 0% center; }
}
</style>
""", unsafe_allow_html=True)

# ── Mode Selector (only when no mode chosen) ──
if st.session_state.selected_mode is None:
    st.markdown('<div class="mode-section"><h3>Select AI Personality</h3></div>', unsafe_allow_html=True)

    cols = st.columns(3, gap="medium")
    mode_keys = list(MODES.keys())

    for i, key in enumerate(mode_keys):
        mode_data = MODES[key]
        with cols[i]:
            st.markdown(f"""
                <div class="mode-card" id="mode-{key}" onclick="selectMode('{key}')">
                    <span class="emoji">{mode_data['emoji']}</span>
                    <span class="label">{mode_data['label']}</span>
                </div>
            """, unsafe_allow_html=True)

            if st.button(
                f"{mode_data['emoji']} {mode_data['label']}",
                key=f"btn_{key}",
                use_container_width=True,
                type="secondary"
            ):
                st.session_state.selected_mode = key
                st.session_state.messages = [
                    SystemMessage(content=MODES[key]["system"])
                ]
                st.rerun()

    st.markdown("""
    <script>
    function selectMode(mode) {
        // Visual feedback for mode cards
        document.querySelectorAll('.mode-card').forEach(c => c.classList.remove('active'));
        document.getElementById('mode-' + mode).classList.add('active');
    }
    </script>
    """, unsafe_allow_html=True)

else:
    # ── Active Mode Badge & Reset ──
    mode_key = st.session_state.selected_mode
    mode_data = MODES[mode_key]

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"""
            <div class="mode-badge {mode_data['badge_class']}">
                {mode_data['emoji']} {mode_data['label']} Mode Active
            </div>
        """, unsafe_allow_html=True)
    with col3:
        if st.button("🔄 Change", key="change_mode"):
            reset_chat()

    # ── Chat Container ──
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    # Welcome message if no conversation yet
    if len(st.session_state.messages) <= 1:
        st.markdown(f"""
            <div class="welcome-banner">
                <h2>Hey there! 👋</h2>
                <p>I'm in <strong>{mode_data['emoji']} {mode_data['label']}</strong> mode. 
                Say something and I'll respond accordingly!</p>
            </div>
        """, unsafe_allow_html=True)

    # Render all messages
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            render_message("user", msg.content)
        elif isinstance(msg, AIMessage):
            render_message("bot", msg.content)

    # Typing indicator
    if st.session_state.typing:
        render_typing_indicator()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Input Area ──
    with st.container():
        user_input = st.text_area(
            "Type your message...",
            key="chat_input",
            placeholder="Type your message here... (type '0' to exit)",
            height=50,
            label_visibility="collapsed"
        )

        col_send, col_clear = st.columns([6, 1])
        with col_send:
            send_clicked = st.button("Send ➤", key="send_btn", use_container_width=True)
        with col_clear:
            if st.button("🗑️", key="clear_btn"):
                st.session_state.messages = [
                    SystemMessage(content=MODES[mode_key]["system"])
                ]
                st.rerun()

    # ── Handle Send ──
    if (send_clicked and user_input.strip()) or (user_input.strip() and st.session_state.get("_last_input") != user_input):
        if user_input.strip() == "0":
            st.session_state.messages.append(AIMessage(content="Goodbye! Feel free to come back anytime! 👋"))
            st.success("Chat ended. Change mode to start fresh!")
            st.stop()

        # Append user message
        st.session_state.messages.append(HumanMessage(content=user_input.strip()))

        # Show typing indicator
        st.session_state.typing = True
        st.session_state._last_input = user_input
        st.rerun()

    # Actually get the response (after typing indicator shows)
    if st.session_state.typing and st.session_state.messages and isinstance(st.session_state.messages[-1], HumanMessage):
        time.sleep(0.5)  # Simulate thinking
        try:
            response = st.session_state.model.invoke(st.session_state.messages)
            st.session_state.messages.append(AIMessage(content=response.content))
        except Exception as e:
            st.session_state.messages.append(AIMessage(content=f"⚠️ Error: {str(e)}"))
        
        st.session_state.typing = False
        st.rerun()

# ──────────────────────────────────────────────
# 7. Footer
# ──────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 20px 0 10px; color: rgba(255,255,255,0.2); font-size: 11px;">
    Powered by Mistral AI &bull; Built with Streamlit
</div>
""", unsafe_allow_html=True)


