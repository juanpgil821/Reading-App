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

    /* Readable text blocks - FONT SIZE INCREASED BY 2PT */
    .stMarkdown, p, .stMetric, [data-testid="stMetricValue"] {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        padding: 15px !important;
        border-radius: 20px !important;
        color: #4B0082 !important;
        border: 2px solid #FFB6C1;
        margin-bottom: 10px;
        font-size: 20px !important; 
    }}

    h1 {{ font-size: 34px !important; }}
    h2 {{ font-size: 30px !important; }}
    h3 {{ font-size: 26px !important; }}

    /* Buttons Style */
    .stButton>button {{
        background-color: #FF69B4 !important;
        color: white !important;
        border-radius: 25px !important;
        border: 2px solid #FF1493 !important;
        font-size: 20px !important; /* Increased font */
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
        height: 60px; /* Increased height for bigger text */
        background-color: #FFF0F5;
        border-radius: 10px;
        color: #FF69B4;
        font-weight: bold;
        font-size: 18px !important;
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

# ---------- SIDEBAR ----------
st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxc_Qp9yWtTxWjpE0NaMiPh2SgWSSwZEp1zw&s", caption="✨ Your Royal Guide")
# IMAGEN DEL AXOLOTL (RESTAURADA)
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
    
    # NUEVA ESTRUCTURA DE 3 PESTAÑAS (Icono de bolsa de dinero para Money Master)
    tab1, tab2, tab3 = st.tabs(["🦄 Fantasy World", "📱 Real Life Stories", "💰 Money Master"])
    
    with tab1:
        st.markdown("### ✨ Magic & Adventure")
        fan_stories = [s for s in stories if s.get("category") == "Fantasy"]
        for s in fan_stories: render_story_card(s)
            
    with tab2:
        st.markdown("### 🏫 Life Lessons")
        real_stories = [s for s in stories if s.get("category") == "Realism"]
        for s in real_stories: render_story_card(s)

    with tab3:
        st.markdown("### 💰 Money Master")
        fin_stories = [s for s in stories if s.get("category") == "Financial Literacy"]
        if not fin_stories:
            st.info("New stories coming soon! 💰")
        for s in fin_stories: render_story_card(s)

def render_story_card(story):
    is_completed = story["id"] in progress["stories_completed"]
    btn_label = f"{story['title']} {'✅' if is_completed else '⭐'}"
    if st.button(btn_label, key=f"btn_{story['id']}"):
        st.session_state.current_story = story
        st.session_state.page = "reading"
        st.session_state.score = 0
        st.session_state.question_index = 0
        st.session_state.answer_submitted = False
        st.session_state.reward_given = False
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
    
    q_type = q.get("type", "multiple") 
    user_answer = None

    if q_type == "multiple":
        user_answer = st.radio("Pick one:", q["options"], key=f"quiz_{q_index}")
    elif q_type == "boolean":
        user_answer = st.radio("Is this true?", ["True", "False"], key=f"quiz_{q_index}")
    elif q_type == "thought":
        user_answer = st.text_area("Write your thoughts here...", key=f"quiz_{q_index}")

    if not st.session_state.answer_submitted:
        if st.button("Check Answer"):
            if q_type == "thought" and not user_answer.strip():
                st.warning("Please write something before submitting!")
            else:
                st.session_state.answer_submitted = True
                st.rerun()
    else:
        is_correct = False
        if q_type == "thought":
            st.success("Great reflection! Points earned. 🌸")
            is_correct = True
        else:
            if user_answer == q["answer"]:
                st.success("Perfect! You got it right! 🌟")
                is_correct = True
            else:
                st.error(f"Not quite! The answer was: {q['answer']}")
        
        if st.button("Next ➡️"):
            progress["total_answers"] += 1
            if is_correct:
                st.session_state.score += 1
                progress["correct_answers"] += 1
            st.session_state.question_index += 1
            st.session_state.answer_submitted = False
            st.rerun()

def result():
    story = st.session_state.current_story
    score = st.session_state.score
    total_q = len(story["questions"])

    st.title("Well Done! 🎉")
    st.write(f"You completed '{story['title']}' with {score}/{total_q} points!")

    if not st.session_state.reward_given:
        if story["id"] not in progress["stories_completed"]:
            earned_points = 10 + (score * 2)
            progress["points"] += earned_points
            progress["total_points_earned"] += earned_points
            progress["stories_completed"].append(story["id"])
            update_streak()
            st.balloons()
            st.success(f"You earned {earned_points} EdiCoins!")
            check_level_up(progress)
        else:
            st.warning("You've already mastered this story!")
        
        save_progress(progress)
        st.session_state.reward_given = True

    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.rerun()

def admin():
    st.title("👨‍👧 Parent Dashboard")
    accuracy = (progress["correct_answers"] / progress["total_answers"] * 100) if progress["total_answers"] > 0 else 0
    st.metric("Spendable EdiCoins", progress['points'])
    st.metric("Lifetime XP (Level)", progress['total_points_earned'])
    st.write(f"Shields (Streak Savers): {progress.get('streak_saver', 0)}")
    st.write(f"Stories completed: {len(progress['stories_completed'])}")
    st.write(f"Accuracy: {round(accuracy, 2)}%")

# ---------- NAVIGATION ----------
if menu == "Parent Dashboard":
    pwd = st.sidebar.text_input("Password", type="password")
    if pwd == "1234": admin()
    else: st.sidebar.warning("Restricted Area")
elif menu == "Badges":
    show_missions(progress)
elif menu == "Edi-Mar-Ket":
    show_market(progress, save_progress)
else:
    if st.session_state.page == "home": home()
    elif st.session_state.page == "reading": reading()
    elif st.session_state.page == "quiz": quiz()
    elif st.session_state.page == "result": result()

