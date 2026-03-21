import streamlit as st
from datetime import date, timedelta
from stories import stories
import pandas as pd

# ---------- 1. DISEÑO MÁGICO (CSS) ----------
st.set_page_config(page_title="Castillo de Lectura", layout="centered")

st.markdown(
    """
    <style>
    /* Fondo del Castillo y Arcoíris */
    .stApp {
        background-image: url("http://googleusercontent.com/image_collection/image_retrieval/12879231435778618406_0");
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
    }
    /* Botones Rosa Princesa */
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
    /* Menú lateral Rosa Claro */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 240, 245, 0.95);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- 2. INICIALIZACIÓN DE DATOS (MANUAL) ----------
if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "name": "Princesa",
        "points": 0,
        "streak": 0,
        "last_read_date": "2024-01-01",
        "stories_completed": [],
        "total_answers": 0,
        "correct_answers": 0
    }

progress = st.session_state.user_data

# Estados de navegación y quiz
if "page" not in st.session_state: st.session_state.page = "home"
if "current_story" not in st.session_state: st.session_state.current_story = None
if "score" not in st.session_state: st.session_state.score = 0
if "question_index" not in st.session_state: st.session_state.question_index = 0
if "answer_submitted" not in st.session_state: st.session_state.answer_submitted = False

# ---------- 3. LÓGICA DE RACHA ----------
def update_streak():
    today = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))
    last_date = str(progress["last_read_date"])
    
    if last_date == yesterday:
        progress["streak"] += 1
    elif last_date != today:
        progress["streak"] = 1
    progress["last_read_date"] = today

# ---------- 4. BARRA LATERAL (PERSONAJES) ----------
with st.sidebar:
    st.image("http://googleusercontent.com/image_collection/image_retrieval/16477053185621664876_0", caption="👑 Tu Guía Real")
    st.image("http://googleusercontent.com/image_collection/image_retrieval/9666325166192283520_0", width=120)
    st.write("---")
    st.subheader("🔑 Panel de Papá")
    if st.checkbox("Ver progreso"):
        st.write(f"Puntos: {progress['points']}")
        st.write(f"Racha: {progress['streak']}")
        st.write(f"Correctas: {progress['correct_answers']}/{progress['total_answers']}")

# ---------- 5. PÁGINAS DEL JUEGO ----------

def home():
    st.title(f"✨ ¡Hola, {progress['name']}! ✨")
    c1, c2 = st.columns(2)
    c1.metric("💰 EdiCoins", progress['points'])
    c2.metric("🔥 Racha", f"{progress['streak']} días")

    st.subheader("📖 Elige tu aventura:")
    for story in stories:
        completada = story["id"] in progress["stories_completed"]
        icono = "✅" if completada else "⭐"
        if st.button(f"{icono} {story['title']}", key=f"btn_{story['id']}"):
            st.session_state.current_story = story
            st.session_state.page = "reading"
            st.session_state.score = 0
            st.session_state.question_index = 0
            st.session_state.answer_submitted = False
            st.rerun()

def reading():
    story = st.session_state.current_story
    st.title(story["title"])
    st.write(story["text"])
    if st.button("✨ ¡Ya terminé de leer! ✨"):
        st.session_state.page = "quiz"
        st.rerun()

def quiz():
    story = st.session_state.current_story
    idx = st.session_state.question_index
    preguntas = story["questions"]

    if idx >= len(preguntas):
        st.session_state.page = "result"
        st.rerun()
        return

    q = preguntas[idx]
    st.subheader(f"Pregunta {idx + 1} de {len(preguntas)}")
    st.write(q["question"])
    
    opcion = st.radio("Selecciona tu respuesta:", q["options"], key=f"quiz_opt_{idx}")

    if not st.session_state.answer_submitted:
        if st.button("Enviar respuesta"):
            st.session_state.answer_submitted = True
            st.rerun()
    else:
        if opcion == q["answer"]:
            st.success("¡Excelente! Es correcto. 🌟")
        else:
            st.error(f"Casi... la respuesta era: {q['answer']}")
        
        if st.button("Siguiente ➡️"):
            progress["total_answers"] += 1
            if opcion == q["answer"]:
                st.session_state.score += 1
                progress["correct_answers"] += 1
            st.session_state.question_index += 1
            st.session_state.answer_submitted = False
            st.rerun()

def result():
    story = st.session_state.current_story
    st.title("¡Lectura Completada! 🎉")
    
    # Solo damos puntos si no la había completado en esta sesión
    if story["id"] not in progress["stories_completed"]:
        puntos_ganados = 10 + (st.session_state.score * 5)
        progress["points"] += puntos_ganados
        progress["stories_completed"].append(story["id"])
        update_streak()
        st.balloons()
        st.success(f"¡Has ganado {puntos_ganados} EdiCoins! 💰")
    else:
        st.info("¡Gracias por leerla de nuevo! Esta ya la tenías dominada.")

    st.write(f"Aciertos: {st.session_state.score} de {len(story['questions'])}")
    if st.button("Volver al Inicio"):
        st.session_state.page = "home"
        st.rerun()

# ---------- NAVEGACIÓN PRINCIPAL ----------
if st.session_state.page == "home": home()
elif st.session_state.page == "reading": reading()
elif st.session_state.page == "quiz": quiz()
elif st.session_state.page == "result": result()
