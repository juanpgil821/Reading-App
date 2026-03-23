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
    /* Pink Castle Background */
    .stApp {{
        background-image: url("https://icon2.cleanpng.com/lnd/20240424/yql/transparent-disney-castle-pink-disney-castle-on-rocky-outcropping-by-water66288f03215b63.27749470.webp");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* Readable text blocks (cloud/parchment style) */
    .stMarkdown, p, h1, h2, h3, .stMetric, [data-testid="stMetricValue"] {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        padding: 15px !important;
        border-radius: 20px !important;
        color: #4B0082 !important;
        border: 2px solid #FFB6C1;
        margin-bottom: 10px;
    }}

    /* Princess Pink Buttons */
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

    /* Light Pink Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: rgba(255, 240, 245, 0.95);
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- LOAD PROGRESS ----------
def load_progress():
    try:
        with open("progress.json", "r") as f:
            data = json.load(f)
            # Aseguramos que existan las nuevas llaves para niveles
            if "total_points_earned" not in data:
                data["total_points_earned"] = data.get("points", 0)
            return data
    except FileNotFoundError:
        return {
            "name": "Princess",
            "points": 0,
            "total_points_earned": 0, # Puntos totales para niveles
            "streak": 0,
            "last_read_date": "",
            "stories_completed": [],
            "total_answers": 0,
            "correct_answers": 0
        }

def save_progress(data):
    with open("progress.json", "w") as f:
        json.dump(data, f, indent=4)

if "user_data" not in st.session_state:
    st.session_state.user_data = load_progress()

progress = st.session_state.user_data

# ---------- SESSION STATE ----------
if "page" not in st.session_state: st.session_state.page = "home"
if "current_story" not in st.session_state: st.session_state.current_story = None
if "score" not in st.session_state: st.session_state.score = 0
if "question_index" not in st.session_state: st.session_state.question_index = 0
if "answer_submitted" not in st.session_state: st.session_state.answer_submitted = False
if "reward_given" not in st.session_state: st.session_state.reward_given = False

# ---------- LOGIC: UPDATE STREAK ----------
def update_streak():
    today = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))
    
    if progress["last_read_date"] == yesterday:
        progress["streak"] += 1
    elif progress["last_read_date"] != today:
        progress["streak"] = 1
    
    progress["last_read_date"] = today
    save_progress(progress)

# ---------- SIDEBAR (CHARACTERS & NAVIGATION) ----------
st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxc_Qp9yWtTxWjpE0NaMiPh2SgWSSwZEp1zw&s", caption="✨ Your Royal Guide")
st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSSn8LZwdDg8oDeke6JTT0i9yjpW4nNRLMq0Q&s", width=120)

# Mostrar Nivel actual en el Sidebar
current_level = get_current_level(progress["total_points_earned"])
st.sidebar.markdown(f"### Rank: {current_level['icon']} {current_level['name']}")

st.sidebar.title("Magical Menu")
menu = st.sidebar.radio("Go to:", ["Home", "Badges", "Edi-Mar-Ket", "Parent Dashboard"])

# ---------- PAGES ----------

def home():
    st.title(f"✨ Welcome, {progress['name']}! ✨")
    
    # Interfaz de Niveles (Barra de progreso)
    show_level_ui(progress)
    
    col1, col2 = st.columns(2)
    col1.metric("💰 EdiCoins", progress['points'])
    col2.metric("🔥 Streak", f"{progress['streak']} days")

    st.subheader("Your Stories")
    for story in stories:
        is_completed = story["id"] in progress["stories_completed"]
        label = f"{story['title']} {'✅' if is_completed else '⭐'}"
        
        if st.button(label, key=story["id"]):
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
    st.write(q["question"])
    
    answer = st.radio("Choose an answer:", q["options"], key=f"radio_{q_index}")

    if not st.session_state.answer_submitted:
        if st.button("Submit Answer"):
            st.session_state.answer_submitted = True
            st.rerun()
    else:
        if answer == q["answer"]:
            st.success("Excellent! That's correct. 🌟")
        else:
            st.error(f"Almost! The answer was: {q['answer']}")
        
        if st.button("Next ➡️"):
            progress["total_answers"] += 1
            if answer == q["answer"]:
                st.session_state.score += 1
                progress["correct_answers"] += 1
            
            st.session_state.question_index += 1
            st.session_state.answer_submitted = False
            st.rerun()

def result():
    story = st.session_state.current_story
    score = st.session_state.score
    total_q = len(story["questions"])

    st.title("Final Results! 🎉")
    st.write(f"You got {score} out of {total_q} correct.")

    if not st.session_state.reward_given:
        if story["id"] not in progress["stories_completed"]:
            earned_points = 10 + (score * 2)
            
            # ACTUALIZACIÓN DE PUNTOS (Gastrables y Totales para niveles)
            progress["points"] += earned_points
            progress["total_points_earned"] += earned_points
            
            progress["stories_completed"].append(story["id"])
            update_streak()
            st.balloons()
            st.success(f"You earned {earned_points} EdiCoins! (10 for reading and {score * 2} for your answers)")
            
            # Verificar si subió de nivel (Lógica de levels.py)
            check_level_up(progress)
        else:
            st.warning("You already completed this story! Keep practicing to earn more in new stories.")
        
        save_progress(progress)
        st.session_state.reward_given = True

    st.markdown(f"**💰 Total EdiCoins:** {progress['points']}")
    
    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.rerun()

def admin():
    st.title("👨‍👧 Parent Dashboard")
    accuracy = (progress["correct_answers"] / progress["total_answers"] * 100) if progress["total_answers"] > 0 else 0
    st.metric("Spendable EdiCoins", progress['points'])
    st.metric("Lifetime XP (Level)", progress['total_points_earned'])
    st.write(f"Stories completed: {len(progress['stories_completed'])}")
    st.write(f"Accuracy: {round(accuracy, 2)}%")

# ---------- NAVIGATION LOGIC ----------
if menu == "Parent Dashboard":
    password = st.sidebar.text_input("Password", type="password")
    if password == "1234":
        admin()
    else:
        st.sidebar.warning("Incorrect password")
elif menu == "Badges":
    show_missions(progress)
elif menu == "Edi-Mar-Ket":
    show_market(progress, save_progress)
else:
    if st.session_state.page == "home": home()
    elif st.session_state.page == "reading": reading()
    elif st.session_state.page == "quiz": quiz()
    elif st.session_state.page == "result": result()
 
