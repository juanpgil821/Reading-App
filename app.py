import streamlit as st
import json
from stories import stories

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

# ---------- HOME ----------
def home():
    st.title(f"📚 Welcome, {progress['name']}!")

    st.write(f"🪙 EdiCoins: {progress['points']}")
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

    if q_index < len(story["questions"]):
        q = story["questions"][q_index]

        st.subheader(q["question"])
        answer = st.radio("Choose an answer:", q["options"])

        if st.button("Submit"):
            progress["total_answers"] += 1

            if answer == q["answer"]:
                st.success("Correct! 🎉")
                st.session_state.score += 1
                progress["correct_answers"] += 1
            else:
                st.error(f"Wrong! The correct answer was: {q['answer']}")

            st.session_state.question_index += 1
    else:
        st.session_state.page = "result"

# ---------- RESULT ----------
def result():
    story = st.session_state.current_story
    total_q = len(story["questions"])
    score = st.session_state.score

    st.title("Results")

    st.write(f"You got {score} out of {total_q}")

    earned_points = 10 + (score * 5)
    progress["points"] += earned_points

    if story["id"] not in progress["stories_completed"]:
        progress["stories_completed"].append(story["id"])

    save_progress(progress)

    if score == total_q:
        st.success("🔥 Amazing! You're a reading star!")
    else:
        st.info("✨ Good job! Keep improving!")

    if st.button("Back to Home"):
        st.session_state.page = "home"

# ---------- ADMIN DASHBOARD ----------
def admin():
    st.title("👨‍👧 Parent Dashboard")

    accuracy = 0
    if progress["total_answers"] > 0:
        accuracy = (progress["correct_answers"] / progress["total_answers"]) * 100

    st.write(f"🪙 EdiCoins: {progress['points']}")
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
