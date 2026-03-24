import streamlit as st
import json
from datetime import date, timedelta
from stories import stories
from market import show_market
from missions import show_missions
from levels import show_level_ui, check_level_up, get_current_level

# ---------- MAGICAL VISUAL CONFIGURATION (CSS) ----------
st.set_page_config(page_title="The Reading Castle", layout="centered")

st.markdown(
    f"""
    <style>
    /* Background */
    .stApp {{
        background-image: url("https://icon2.cleanpng.com/lnd/20240424/yql/transparent-disney-castle-pink-disney-castle-on-rocky-outcropping-by-water66288f03215b63.27749470.webp");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* Readable text blocks */
    .stMarkdown, p, h1, h2, h3, .stMetric, [data-testid="stMetricValue"] {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        padding: 15px !important;
        border-radius: 20px !important;
        color: #4B0082 !important;
        border: 2px solid #FFB6C1;
        margin-bottom: 10px;
    }}

    /* Buttons Style */
    .stButton>button {{
        background-color: #FF69B4 !important;
        color: white !important;
        border-radius: 25px !important;
        border: 2px solid #FF1493 !important;
        font-size: 18px !important;
        font-weight: bold !important;
        width: 100%;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        transform: scale(1.03);
        background-color: #FF1493 !important;
    }}

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        background-color: rgba(255, 255, 255, 0.7);
        padding: 10px;
        border-radius: 15px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        background-color: #FFF0F5;
        border-radius: 10px;
        color: #FF69B4;
        font-weight: bold;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #FFB6C1 !important;
        color: white !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- LOAD/SAVE PROGRESS ----------
def load_progress():
    try:
        with open("progress.json", "r") as f:
            data = json.load(f)
            if "total_points_earned" not in data: data["total_points_earned"] = data.get("points", 0)
            if "last_level_seen" not in data: data["last_level_seen"] = 1
            if "streak_saver" not in data: data["streak_saver"] = 0
            return data
    except FileNotFoundError:
        return {
            "name": "Princess", "points": 0, "total_points_earned": 0,
            "last_level_seen": 1, "streak_saver": 0, "streak": 0,
            "last_read_date": "", "stories_completed": [],
            "total_answers": 0, "correct_answers": 0
        }

def save_progress(data):
    with open("progress.json", "w") as f:
        json.dump(data, f, indent=4)

if "user_data" not in st.session_state:
    st.session_state.user_data = load_progress()

progress = st.session_state.user_data

# ---------- SESSION STATES ----------
if "page" not in st.session_state: st.session_state.page = "home"
if "current_story" not in st.session_state: st.session_state.current_story = None
if "score" not in st.session_state: st.session_state.score = 0
if "question_index" not in st.session_state: st.session_state.question_index = 0
if "answer_submitted" not in st.session_state: st.session_state.answer_submitted = False
if "reward_given" not in st.session_state: st.session_state.reward_given = False

def update_streak():
    today = date.today()
    yesterday = today - timedelta(days=1)
    last_date_str = progress.get("last_read_date", "")
    if last_date_str == str(today): return
    if last_date_str == str(yesterday):
        progress["streak"] += 1
    else:
        if progress.get("streak_saver", 0) > 0:
            progress["streak_saver"] -= 1
            progress["streak"] += 1
            st.warning("🛡️ STREAK SAVED! You used a protective shield.")
        else:
            progress["streak"] = 1
    progress["last_read_date"] = str(today)
    save_progress(progress)

# ---------- SIDEBAR (RESTORED AXOLOTL) ----------
st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxc_Qp9yWtTxWjpE0NaMiPh2SgWSSwZEp1zw&s",
