import streamlit as st
import json
from stories import stories
from datetime import date, timedelta
import os  # agregado para persistencia en Streamlit Cloud

# ---------- LOAD / SAVE PROGRESS (persistente) ----------
PROGRESS_FILE = "/mnt/data/progress.json"

DEFAULT_PROGRESS = {
    "name": "Edimar",
    "points": 0,
    "streak": 0,
    "stories_completed": [],
    "total_answers": 0,
    "correct_answers": 0,
    "last_read_date": None
}

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    else:
        # Inicializa progreso por primera vez
        save_progress(DEFAULT_PROGRESS)
        return DEFAULT_PROGRESS.copy()

def save_progress(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=4)

progress = load_progress()

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

if "last_answer" not in st.session_state:
    st.session_state.last_answer = None

if "points_added" not in st.session_state:
    st.session_state.points_added = False

# ---------- HOME ----------
def home():
    st.title(f"📚 Welcome, {progress['name']}!")

    st.markdown(f"**💰 EdiCoins:** {progress['points']}")
    st.write(f"🔥 Streak: {progress['streak']} days")

    st.subheader("Stories")

    for story in stories:
        if story["id"] in progress["stories_completed"]:
            status = "✅ Completed"
        else:
            status = "➡️ New"

        if st.button(f"{story['title']} - {status}"):
            st.session_state.current_story = story
            st.session_state.page = "reading"
            st.session_state.score = 0
            st.session_state.question_index = 0
            st.session_state.answer_submitted = False
            st.session_state.last_answer = None
            st.session_state.points_added = False

# ---------- READING ----------
def reading():
    story = st.session_state.current_story

    st.title(story["title"])
    st.write(story["text"])

    if st.button("Start Quiz"):
        st.session_state.page = "quiz"

# ---------- QUIZ ----------
def quiz():
    story = st.session_state.current_story
    q_index = st.session_state.question_index

    if q_index >= len(story["questions"]):
        st.session_state.page = "result"
        result()
        return

    q = story["questions"][q_index]

    st.subheader(q["question"])
    answer = st.radio("Choose an answer:", q["options"], key=f"q_{q_index}")

    if st.button("Submit", key=f"submit_{q_index}"):
        st.session_state.last_answer = answer
        st.session_state.answer_submitted = True

    if st.session_state.answer_submitted:
        if st.button("Next", key=f"next_{q_index}"):
            progress["total_answers"] += 1
            if st.session_state.last_answer == q["answer"]:
                st.success("Correct! 🎉")
                st.session_state.score += 1
                progress["correct_answers"] += 1
            else:
                st.error(f"Wrong! The correct answer was: {q['answer']}")

            st.session_state.question_index += 1
            st.session_state.answer_submitted = False
            st.session_state.last_answer = None

# ---------- RESULT ----------
def result():
    story = st.session_state.current_story
    total_q = len(story["questions"])
    score = st.session_state.score

    st.title("Results")
    st.write(f"You got {score} out of {total_q}")

    # ---------- POINTS (PATCH: solo sumar si primera vez y no repetir capítulo) ----------
    if not st.session_state.points_added and story["id"] not in progress["stories_completed"]:
        earned_points = 10 + (score * 5)
        progress["points"] += earned_points
        st.session_state.points_added = True

        # ---------- STREAK ----------
        today = date.today()
        last_read_str = progress.get("last_read_date", None)
        if last_read_str:
            last_read = date.fromisoformat(last_read_str)
        else:
            last_read = today - timedelta(days=1)

        if today == last_read + timedelta(days=1):
            progress["streak"] += 1
        elif today > last_read + timedelta(days=1):
            progress["streak"] = 1

        progress["last_read_date"] = str(today)

        # Evita duplicados en stories_completed
        if story["id"] not in progress["stories_completed"]:
            progress["stories_completed"].append(story["id"])

        save_progress(progress)

    st.markdown(f"**💰 EdiCoins:** {progress['points']}")

    if score == total_q:
        st.success("🔥 Amazing! You're a reading star!")
    else:
        st.info("✨ Good job! Keep improving!")

    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.session_state.points_added = False
        save_progress(progress)  # asegura persistencia al volver a Home

# ---------- ADMIN DASHBOARD ----------
def admin():
    st.title("👨‍👧 Parent Dashboard")

    accuracy = 0
    if progress["total_answers"] > 0:
        accuracy = (progress["correct_answers"] / progress["total_answers"]) * 100

    st.markdown(f"**💰 EdiCoins:** {progress['points']}")
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
    if st.session_state.page == "home":
        home()
    elif st.session_state.page == "reading":
        reading()
    elif st.session_state.page == "quiz":
        quiz()
    elif st.session_state.page == "result":
        result()
