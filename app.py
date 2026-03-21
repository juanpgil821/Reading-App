import streamlit as st
import json
from datetime import date, timedelta
from stories import stories

# ---------- LOAD PROGRESS ----------
def load_progress():
    try:
        with open("progress.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Valores iniciales por defecto si el archivo no existe
        return {
            "name": "Explorer",
            "points": 0,
            "streak": 0,
            "last_read_date": "",
            "stories_completed": [],
            "total_answers": 0,
            "correct_answers": 0
        }

def save_progress(data):
    with open("progress.json", "w") as f:
        json.dump(data, f, indent=4)

# Cargamos el progreso al inicio
if "user_data" not in st.session_state:
    st.session_state.user_data = load_progress()

progress = st.session_state.user_data

# ---------- SESSION STATE ----------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "current_story" not in st.session_state:
    st.session_state.current_story = None
if "score" not in st.session_state:
    st.session_state.score = 0
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "answer_submitted" not in st.session_state:
    st.session_state.answer_submitted = False
if "reward_given" not in st.session_state:
    st.session_state.reward_given = False

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

# ---------- HOME ----------
def home():
    st.title(f"📚 Welcome, {progress['name']}!")
    col1, col2 = st.columns(2)
    col1.metric("💰 EdiCoins", progress['points'])
    col2.metric("🔥 Streak", f"{progress['streak']} days")

    st.subheader("Your Stories")
    for story in stories:
        is_completed = story["id"] in progress["stories_completed"]
        label = f"{story['title']} {'✅' if is_completed else '➡️'}"
        
        if st.button(label, key=story["id"]):
            st.session_state.current_story = story
            st.session_state.page = "reading"
            st.session_state.score = 0
            st.session_state.question_index = 0
            st.session_state.answer_submitted = False
            st.session_state.reward_given = False
            st.rerun()

# ---------- READING ----------
def reading():
    story = st.session_state.current_story
    st.title(story["title"])
    st.write(story["text"])
    if st.button("Start Quiz"):
        st.session_state.page = "quiz"
        st.rerun()

# ---------- QUIZ ----------
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
            st.success("Correct! 🎉")
        else:
            st.error(f"Wrong! The correct answer was: {q['answer']}")
        
        if st.button("Next"):
            # Procesar puntos internamente antes de pasar
            progress["total_answers"] += 1
            if answer == q["answer"]:
                st.session_state.score += 1
                progress["correct_answers"] += 1
            
            st.session_state.question_index += 1
            st.session_state.answer_submitted = False
            st.rerun()

# ---------- RESULT ----------
def result():
    story = st.session_state.current_story
    score = st.session_state.score
    total_q = len(story["questions"])

    st.title("Results")
    st.write(f"You got {score} out of {total_q}")

    # LÓGICA DE PREMIOS (Solo se ejecuta una vez por sesión de lectura)
    if not st.session_state.reward_given:
        if story["id"] not in progress["stories_completed"]:
            earned_points = 10 + (score * 5)
            progress["points"] += earned_points
            progress["stories_completed"].append(story["id"])
            update_streak() # Solo sube el streak si completa una historia nueva
            st.balloons()
        else:
            st.warning("Story already completed. No extra EdiCoins this time, but thanks for practicing!")
        
        save_progress(progress)
        st.session_state.reward_given = True

    st.markdown(f"**💰 EdiCoins:** {progress['points']}")
    
    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.rerun()

# ---------- ADMIN DASHBOARD ----------
def admin():
    st.title("👨‍👧 Parent Dashboard")
    accuracy = (progress["correct_answers"] / progress["total_answers"] * 100) if progress["total_answers"] > 0 else 0
    st.metric("Total Points", progress['points'])
    st.write(f"Stories completed: {len(progress['stories_completed'])}")
    st.write(f"Accuracy: {round(accuracy, 2)}%")

# ---------- NAVIGATION ----------
st.sidebar.title("Menu")
menu = st.sidebar.radio("Go to", ["Home", "Parent Dashboard"])

if menu == "Parent Dashboard":
    password = st.sidebar.text_input("Enter password", type="password")
    if password == "1234":
        admin()
    else:
        st.sidebar.warning("Wrong password")
else:
    if st.session_state.page == "home": home()
    elif st.session_state.page == "reading": reading()
    elif st.session_state.page == "quiz": quiz()
    elif st.session_state.page == "result": result()
