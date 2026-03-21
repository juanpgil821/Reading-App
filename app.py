import streamlit as st
from streamlit_gsheets import GSheetsConnection
from datetime import date, timedelta
from stories import stories
import pandas as pd

# ---------- CONEXIÓN A GOOGLE SHEETS ----------
# Esto usa los "Secrets" que pegaste en Streamlit Cloud
conn = st.connection("gsheets", type=GSheetsConnection)

def load_progress():
    try:
        # Lee la hoja llamada "Lectura_App"
        df = conn.read(worksheet="Lectura_App", ttl=0)
        data = df.iloc[0].to_dict()
        
        # Convertimos la celda de historias de texto "1,2" a lista [1, 2]
        if pd.isna(data["stories_completed"]) or str(data["stories_completed"]).strip() == "":
            data["stories_completed"] = []
        else:
            data["stories_completed"] = [int(i) for i in str(data["stories_completed"]).split(",") if i.strip()]
        return data
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return None

def save_progress_to_sheets(data):
    # Convertimos la lista de vuelta a texto para Excel
    stories_str = ",".join(map(str, data["stories_completed"]))
    
    # Preparamos la fila única para actualizar
    updated_df = pd.DataFrame([{
        "name": data["name"],
        "points": int(data["points"]),
        "streak": int(data["streak"]),
        "last_read_date": str(data["last_read_date"]),
        "stories_completed": stories_str,
        "total_answers": int(data["total_answers"]),
        "correct_answers": int(data["correct_answers"])
    }])
    
    # Actualizamos la hoja
    conn.update(worksheet="Lectura_App", data=updated_df)

# ---------- INICIALIZACIÓN ----------
if "user_data" not in st.session_state:
    st.session_state.user_data = load_progress()

progress = st.session_state.user_data

# Estados de navegación
if "page" not in st.session_state: st.session_state.page = "home"
if "current_story" not in st.session_state: st.session_state.current_story = None
if "score" not in st.session_state: st.session_state.score = 0
if "question_index" not in st.session_state: st.session_state.question_index = 0
if "answer_submitted" not in st.session_state: st.session_state.answer_submitted = False
if "reward_given" not in st.session_state: st.session_state.reward_given = False

# ---------- LÓGICA: RACHA (STREAK) ----------
def update_streak():
    today = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))
    if str(progress["last_read_date"]) == yesterday:
        progress["streak"] += 1
    elif str(progress["last_read_date"]) != today:
        progress["streak"] = 1
    progress["last_read_date"] = today

# ---------- PÁGINAS ----------
def home():
    st.title(f"📚 ¡Bienvenida, {progress['name']}!")
    col1, col2 = st.columns(2)
    col1.metric("💰 EdiCoins", progress['points'])
    col2.metric("🔥 Racha", f"{progress['streak']} días")

    st.subheader("Tus Historias")
    for story in stories:
        is_completed = story["id"] in progress["stories_completed"]
        label = f"{story['title']} {'✅' if is_completed else '➡️'}"
        if st.button(label, key=f"btn_{story['id']}"):
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
    if st.button("Empezar Quiz"):
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
    st.subheader(f"Pregunta {q_index + 1}")
    st.write(q["question"])
    answer = st.radio("Elige una:", q["options"], key=f"r_{q_index}")

    if not st.session_state.answer_submitted:
        if st.button("Enviar"):
            st.session_state.answer_submitted = True
            st.rerun()
    else:
        if answer == q["answer"]: st.success("¡Correcto! 🎉")
        else: st.error(f"Incorrecto. Era: {q['answer']}")
        
        if st.button("Siguiente"):
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
    
    st.title("¡Resultados! 🌟")
    if not st.session_state.reward_given:
        if story["id"] not in progress["stories_completed"]:
            puntos = 10 + (score * 5)
            progress["points"] += puntos
            progress["stories_completed"].append(story["id"])
            update_streak()
            
            # GUARDADO EN LA NUBE
            save_progress_to_sheets(progress)
            st.balloons()
            st.success(f"¡Ganaste {puntos} EdiCoins!")
        else:
            st.warning("Esta historia ya la completaste, ¡pero gracias por practicar!")
        st.session_state.reward_given = True

    if st.button("Volver al Inicio"):
        st.session_state.page = "home"
        st.rerun()

# ---------- NAVEGACIÓN ----------
st.sidebar.title("Menú")
menu = st.sidebar.radio("Ir a", ["Home", "Parent Dashboard"])

if menu == "Parent Dashboard":
    st.title("👨‍👧 Panel de Control")
    if st.sidebar.text_input("Contraseña", type="password") == "1234":
        st.metric("Puntos Totales", progress['points'])
        st.write(f"Historias leídas: {len(progress['stories_completed'])}")
        if st.button("Forzar recarga desde Excel"):
            st.session_state.user_data = load_progress()
            st.rerun()
else:
    if progress:
        if st.session_state.page == "home": home()
        elif st.session_state.page == "reading": reading()
        elif st.session_state.page == "quiz": quiz()
        elif st.session_state.page == "result": result()
