import streamlit as st
import json
from datetime import date, timedelta
from stories import stories

# ---------- CONFIGURACIÓN VISUAL MÁGICA (CSS) ----------
st.set_page_config(page_title="El Castillo de Lectura", layout="centered")

st.markdown(
    f"""
    <style>
    /* Fondo del Castillo Rosa */
    .stApp {{
        background-image: url("https://icon2.cleanpng.com/lnd/20240424/yql/transparent-disney-castle-pink-disney-castle-on-rocky-outcropping-by-water66288f03215b63.27749470.webp");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* Bloques de texto legibles (estilo nube/pergamino) */
    .stMarkdown, p, h1, h2, h3, .stMetric, [data-testid="stMetricValue"] {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        padding: 15px !important;
        border-radius: 20px !important;
        color: #4B0082 !important;
        border: 2px solid #FFB6C1;
        margin-bottom: 10px;
    }}

    /* Botones Rosa Princesa */
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

    /* Menú lateral Rosa Claro */
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
            return json.load(f)
    except FileNotFoundError:
        return {
            "name": "Princesa",
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

# ---------- BARRA LATERAL (PERSONAJES) ----------
st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxc_Qp9yWtTxWjpE0NaMiPh2SgWSSwZEp1zw&s", caption="✨ Tu Guía Real")
st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSSn8LZwdDg8oDeke6JTT0i9yjpW4nNRLMq0Q&s", width=120)
st.sidebar.title("Menú Mágico")
menu = st.sidebar.radio("Ir a:", ["Inicio", "Panel de Papá"])

# ---------- HOME ----------
def home():
    st.title(f"✨ ¡Bienvenida, {progress['name']}! ✨")
    col1, col2 = st.columns(2)
    col1.metric("💰 EdiCoins", progress['points'])
    col2.metric("🔥 Racha", f"{progress['streak']} días")

    st.subheader("Tus Historias")
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

# ---------- READING ----------
def reading():
    story = st.session_state.current_story
    st.title(story["title"])
    st.write(story["text"])
    if st.button("✨ Comenzar Trivia ✨"):
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
    st.subheader(f"Pregunta {q_index + 1} de {len(questions)}")
    st.write(q["question"])
    
    answer = st.radio("Elige una respuesta:", q["options"], key=f"radio_{q_index}")

    if not st.session_state.answer_submitted:
        if st.button("Enviar Respuesta"):
            st.session_state.answer_submitted = True
            st.rerun()
    else:
        if answer == q["answer"]:
            st.success("¡Excelente! Es correcto. 🌟")
        else:
            st.error(f"¡Casi! La respuesta era: {q['answer']}")
        
        if st.button("Siguiente ➡️"):
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

    st.title("¡Resultados Finales! 🎉")
    st.write(f"Lograste {score} de {total_q} aciertos.")

    if not st.session_state.reward_given:
        if story["id"] not in progress["stories_completed"]:
            earned_points = 10 + (score * 5)
            progress["points"] += earned_points
            progress["stories_completed"].append(story["id"])
            update_streak()
            st.balloons()
        else:
            st.warning("¡Esta historia ya la habías completado! Sigue practicando para ganar más.")
        
        save_progress(progress)
        st.session_state.reward_given = True

    st.markdown(f"**💰 Total EdiCoins:** {progress['points']}")
    
    if st.button("Volver al Inicio"):
        st.session_state.page = "home"
        st.rerun()

# ---------- ADMIN DASHBOARD ----------
def admin():
    st.title("👨‍👧 Panel de Papá")
    accuracy = (progress["correct_answers"] / progress["total_answers"] * 100) if progress["total_answers"] > 0 else 0
    st.metric("Puntos Totales", progress['points'])
    st.write(f"Historias completadas: {len(progress['stories_completed'])}")
    st.write(f"Precisión: {round(accuracy, 2)}%")

# ---------- NAVIGATION ----------
if menu == "Panel de Papá":
    password = st.sidebar.text_input("Contraseña", type="password")
    if password == "1234":
        admin()
    else:
        st.sidebar.warning("Contraseña incorrecta")
else:
    if st.session_state.page == "home": home()
    elif st.session_state.page == "reading": reading()
    elif st.session_state.page == "quiz": quiz()
    elif st.session_state.page == "result": result()
