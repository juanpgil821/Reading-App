import streamlit as st
import json
from datetime import date, timedelta
from stories import stories
from market import show_market
from missions import show_missions
from levels import show_level_ui, check_level_up, get_current_level

# ---------- MAGICAL VISUAL CONFIGURATION (CSS) ----------
st.set_page_config(page_title="The Reading Castle", layout="centered")

# CAMBIO CRÍTICO: Nueva URL de imagen estable y limpieza de selectores de fondo
st.markdown(
    """
    <style>
    /* 1. Fondo Global: Forzamos la imagen con !important y una URL estable */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=2000&auto=format&fit=crop") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }

    /* 2. Bloques de texto: Separados para no "tapar" el fondo de la app */
    .stMarkdown, p, .stMetric, [data-testid="stMetricValue"], .stTextArea {
        background-color: rgba(255, 255, 255, 0.9) !important;
        padding: 15px !important;
        border-radius: 20px !important;
        color: #4B0082 !important;
        border: 2px solid #FFB6C1;
        margin-bottom: 10px;
    }

    /* 3. Títulos: Solo color y sombra para no generar bloques negros */
    h1, h2, h3 {
        color: #4B0082 !important;
        text-shadow: 2px 2px 4px white !important;
        background: none !important;
    }

    /* Estilo de Botones */
    .stButton>button {
        background-color: #FF69B4 !important;
        color: white !important;
        border-radius: 25px !important;
        border: 2px solid #FF1493 !important;
        font-size: 18px !important;
        font-weight: bold !important;
        width: 100%;
        transition: 0.3s;
    }

    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.7);
        padding: 10px;
        border-radius: 15px;
    }
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
    except (FileNotFoundError, json.JSONDecodeError):
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
            st.warning("🛡️ STREAK SAVED!")
        else:
            progress["streak"] = 1
    progress["last_read_date"] = str(today)
    save_progress(progress)

# ---------- SIDEBAR ----------
st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxc_Qp9yWtTxWjpE0NaMiPh2SgWSSwZEp1zw&s", caption="✨ Your Royal Guide")
st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSSn8LZwdDg8oDeke6JTT0i9yjpW4nNRLMq0Q&s", width=120)

current_level = get_current_level(progress["total_points_earned"])
st.sidebar.markdown(f"### Rank: {current_level['icon']} {current_level['name']}")
st.sidebar.title("Magical Menu")
menu = st.sidebar.radio("Go to:", ["Home", "Badges", "Edi-Mar-Ket", "Parent Dashboard"])

# ---------- PAGES ----------
def home():
    st.title(f"✨ Welcome, {progress['name']}! ✨")
    show_level_ui(progress)
    col1, col2 = st.columns(2)
    col1.metric("💰 EdiCoins", progress['points'])
    col2.metric("🔥 Streak", f"{progress['streak']} days")
    st.subheader("Choose Your Adventure")
    tab1, tab2, tab3 = st.tabs(["🦄 Fantasy World", "📱 Real Life Stories", "💰 Money Master"])
    
    with tab1:
        st.markdown("### ✨ Magic & Adventure")
        for s in [s for s in stories if s.get("category") == "Fantasy"]: render_story_card(s)
    with tab2:
        st.markdown("### 🏫 Life Lessons")
        for s in [s for s in stories if s.get("category") == "Realism"]: render_story_card(s)
    with tab3:
        st.markdown("### 💰 Money Master")
        fin = [s for s in stories if s.get("category") == "Financial Literacy"]
        if not fin: st.info("New stories coming soon! 💰")
        for s in fin: render_story_card(s)

def render_story_card(story):
    is_completed = story["id"] in progress["stories_completed"]
    if st.button(f"{story['title']} {'✅' if is_completed else '⭐'}", key=f"btn_{story['id']}"):
        st.session_state.current_story, st.session_state.page = story, "reading"
        st.session_state.score, st.session_state.question_index = 0, 0
        st.session_state.answer_submitted, st.session_state.reward_given = False, False
        st.rerun()

def reading():
    story = st.session_state.current_story
    st.title(story["title"])
    st.markdown(f"**Value:** {story['value']}")
    st.write(story["text"])
    if st.button("✨ Start Trivia ✨"):
        st.session_state.page = "quiz"
        st.rerun()

def quiz():
    story = st.session_state.current_story
    q_index = st.session_state.question_index
    questions = story["questions"]
    if q_index >= len(questions):
        st.session_state.page = "result"
        st.rerun()
        return
    q = questions[q_index]
    st.subheader(f"Question {q_index + 1} of {len(questions)}")
    st.write(f"### {q['question']}")
    user_answer = st.radio("Pick one:", q["options"] if q.get("type")=="multiple" else ["True", "False"], key=f"q_{q_index}")
    if not st.session_state.answer_submitted:
        if st.button("Check Answer"):
            st.session_state.answer_submitted = True
            st.rerun()
    else:
        if user_answer == q["answer"]: st.success("Perfect! 🌟")
        else: st.error(f"Not quite! Answer: {q['answer']}")
        if st.button("Next ➡️"):
            progress["total_answers"] += 1
            if user_answer == q["answer"]:
                st.session_state.score += 1
                progress["correct_answers"] += 1
            st.session_state.question_index += 1
            st.session_state.answer_submitted = False
            st.rerun()

def result():
    story, score = st.session_state.current_story, st.session_state.score
    total_q = len(story["questions"])
    st.title("Well Done! 🎉")
    st.write(f"Points: {score}/{total_q}")
    if not st.session_state.reward_given:
        if story["id"] not in progress["stories_completed"]:
            earned = 10 + (score * 2)
            progress["points"] += earned
            progress["total_points_earned"] += earned
            progress["stories_completed"].append(story["id"])
            update_streak()
            st.balloons()
            st.success(f"Earned {earned} EdiCoins!")
            check_level_up(progress)
        save_progress(progress)
        st.session_state.reward_given = True
    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.rerun()

def admin():
    st.title("👨‍👧 Parent Dashboard")
    acc = (progress["correct_answers"] / progress["total_answers"] * 100) if progress["total_answers"] > 0 else 0
    st.metric("EdiCoins", progress['points'])
    st.write(f"Accuracy: {round(acc, 2)}%")

# ---------- NAVIGATION ----------
if menu == "Parent Dashboard":
    if st.sidebar.text_input("Password", type="password") == "1234": admin()
    else: st.sidebar.warning("Restricted Area")
elif menu == "Badges": show_missions(progress)
elif menu == "Edi-Mar-Ket": show_market(progress, save_progress)
else:
    if st.session_state.page == "home": home()
    elif st.session_state.page == "reading": reading()
    elif st.session_state.page == "quiz": quiz()
    elif st.session_state.page == "result": result()
