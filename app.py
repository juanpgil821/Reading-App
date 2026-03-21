import streamlit as st
import json
from stories import stories
from datetime import date, timedelta

# ---------- LOAD PROGRESS ----------
def load_progress():
    with open("progress.json", "r") as f:
        return json.load(f)

def save_progress(data):
    with open("progress.json", "w") as f:
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
    if not st.session_state.points_added:
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
