import streamlit as st
import json
from datetime import date, timedelta
from stories import stories

# ---------- 1. ESTILO MÁGICO (CSS) ----------
st.set_page_config(page_title="Castillo de Lectura", layout="centered")

st.markdown(
    """
    <style>
    /* Fondo del Castillo (Imagen de dominio público de un castillo de cuento) */
    .stApp {
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Fairytale_Castle.jpg/1024px-Fairytale_Castle.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Pergaminos para el texto */
    .stMarkdown, p, h1, h2, h3, .stMetric, [data-testid="stMetricValue"] {
        background-color: rgba(255, 255, 255, 0.9) !important;
        padding: 15px !important;
        border-radius: 20px !important;
        color: #4B0082 !important;
        border: 2px solid #FFB6C1;
        margin-bottom: 10px;
    }

    /* Botones Rosa */
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
    .stButton>button:hover {
        transform: scale(1.03);
        background-color: #FF1493 !important;
    }

    /* Menú lateral */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 240, 245, 0.95);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- 2. LÓGICA JSON (Tu código original) ----------
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

# ---------- 3. ESTADOS Y RACHA ----------
if "page" not in st.session_state: st.session_state.page = "home"
if "current_story" not in st.session_state: st.session_state.current_story = None
if "score" not in st.session_state: st.session_state.score = 0
if "question_index" not in st.session_state: st.session_state.question_index = 0
if "answer_submitted" not in st.session_state: st.session_state.answer_submitted = False
if "reward_given" not in st.session_state: st.session_state.reward_given = False

def update_streak():
    today = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))
    if progress["last_read_date"] == yesterday:
        progress["streak"] += 1
    elif progress["last_read_date"] != today:
        progress["streak"] = 1
    progress["last_read_date"] = today
    save_progress(progress)

# ---------- 4. BARRA LATERAL (IMÁGENES FIJAS) ----------
with st.sidebar:
    # Una princesa clásica de cuento (URL de Wikipedia)
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Princess_and_the_Pea.jpg/439px-Princess_and_the_Pea.jpg", 
             caption="👑 Tu Guía Real", use_container_width=True)
    
    # Axolote Rosa (URL de una ilustración de código abierto)
    st.image("https://raw.githubusercontent.com/Tarik-A/axolotl-js/master/assets/axolotl.png", 
             width=150)
    
    st.title("Menú Mágico")
    menu = st.sidebar.radio("Ir a:", ["Inicio", "Panel de Papá"])

# ---------- 5. PÁGINAS ----------
def home():
    st.title(f"✨ ¡Hola, {progress['name']}! ✨")
    c1, c2 = st.columns(2)
    c1.metric("💰 EdiCoins", progress['points'])
    c2.metric("🔥 Racha", f"{progress['streak']} días")

    st.subheader("📖 Elige tu aventura:")
    for story in stories:
        icono = "✅" if story["id"] in progress["stories_completed"] else "⭐"
        if st.button(f"{icono} {story['title']}", key=story["id"]):
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
    if st.button("✨ ¡Ya terminé, quiero mi Trivia! ✨"):
        st.session_state.page = "quiz"
        st.rerun()

def quiz():
    story = st.session_state.current_story
    idx = st.session_state.question_index
    questions = story["questions"]

    if idx >= len(questions):
        st.session_state.page = "result"
        st.rerun()
        return

    q = questions[idx]
    st.subheader(f"Pregunta {idx + 1} de {len(questions)}")
    st.write(q["question"])
    ans = st.radio("Respuesta:", q["options"], key=f"r_{idx}")

    if not st.session_state.answer_submitted:
        if st.button("Enviar Respuesta 🪄"):
            st.session_state.answer_submitted = True
            st.rerun()
    else:
        if ans == q["answer"]: st.success("¡Correcto! 🌟")
        else: st.error(f"Era: {q['answer']}")
        
        if st.button("Siguiente ➡️"):
            progress["total_answers"] += 1
            if ans == q["answer"]:
                st.session_state.score += 1
                progress["correct_answers"] += 1
            st.session_state.question_index += 1
            st.session_state.answer_submitted = False
            st.rerun()

def result():
    story = st.session_state.current_story
    st.title("¡Resultados! 🎉")
    if not st.session_state.reward_given:
        if story["id"] not in progress["stories_completed"]:
            pts = 10 + (st.session_state.score * 5)
            progress["points"] += pts
            progress["stories_completed"].append(story["id"])
            update_streak()
            st.balloons()
        st.session_state.reward_given = True
        save_progress(progress)
    
    if st.button("Volver al Inicio 🏰"):
        st.session_state.page = "home"
        st.rerun()

# ---------- NAVEGACIÓN ----------
if menu == "Panel de Papá":
    if st.sidebar.text_input("Contraseña", type="password") == "1234":
        st.title("👨‍👧 Panel de Papá")
        accuracy = (progress["correct_answers"] / progress["total_answers"] * 100) if progress["total_answers"] > 0 else 0
        st.metric("Puntos", progress['points'])
        st.write(f"Historias leídas: {len(progress['stories_completed'])}")
        st.write(f"Precisión: {round(accuracy, 2)}%")
else:
    if st.session_state.page == "home": home()
    elif st.session_state.page == "reading": reading()
    elif st.session_state.page == "quiz": quiz()
    elif st.session_state.page == "result": result()
