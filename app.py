import streamlit as st
from streamlit_gsheets import GSheetsConnection
from datetime import date, timedelta
from stories import stories
import pandas as pd

# ---------- CONFIGURACIÓN DE PÁGINA ----------
st.set_page_state = "wide"

# ---------- CONEXIÓN A GOOGLE SHEETS ----------
def get_connection():
    # Limpieza automática de la llave privada (por si los Secrets tienen \n de más)
    secret_dict = st.secrets["connections"]["gsheets"].to_dict()
    if "\\n" in secret_dict["private_key"]:
        secret_dict["private_key"] = secret_dict["private_key"].replace("\\n", "\n")
    
    return st.connection("gsheets", type=GSheetsConnection)

conn = get_connection()

def load_progress():
    try:
        # Intentamos leer la hoja usando la URL de los secrets
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        df = conn.read(spreadsheet=url, worksheet="Lectura_App", ttl=0)
        
        if df is None or df.empty:
            st.error("⚠️ La hoja de cálculo está vacía o no se encuentra.")
            return None
            
        data = df.iloc[0].to_dict()
        
        # Conversión de la lista de historias (Celda E)
        stories_val = str(data.get("stories_completed", ""))
        if pd.isna(data["stories_completed"]) or stories_val.strip() == "" or stories_val == "nan":
            data["stories_completed"] = []
        else:
            data["stories_completed"] = [int(i) for i in stories_val.split(",") if i.strip()]
        
        return data
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")
        return None

def save_progress_to_sheets(data):
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        # Convertimos la lista [1, 2] a texto "1,2"
        stories_str = ",".join(map(str, data["stories_completed"]))
        
        # Preparamos la fila para subir
        updated_df = pd.DataFrame([{
            "name": data["name"],
            "points": int(data["points"]),
            "streak": int(data["streak"]),
            "last_read_date": str(data["last_read_date"]),
            "stories_completed": stories_str,
            "total_answers": int(data["total_answers"]),
            "correct_answers": int(data["correct_answers"])
        }])
        
        conn.update(spreadsheet=url, worksheet="Lectura_App", data=updated_df)
    except Exception as e:
        st.error(f"❌ Error al guardar en la nube: {e}")

# ---------- INICIALIZACIÓN DE SESIÓN ----------
if "user_data" not in st.session_state:
    st.session_state.user_data = load_progress()

progress = st.session_state.user_data

# Si no se pudo cargar el progreso, detenemos la app para no romper nada
if progress is None:
    st.warning("Revisa que hayas compartido el Excel con el correo de la cuenta de servicio y que la pestaña se llame 'Lectura_App'.")
    st.stop()

# Estados de navegación
if "page" not in st.session_state: st.session_state.page = "home"
if "current_story" not in st.session_state: st.session_state.current_story = None
if "score" not in st.session_state: st.session_state.score = 0
if "question_index" not in st.session_state: st.session_state.question_index = 0
if "answer_submitted" not in st.session_state: st.session_state.answer_submitted = False
if "reward_given" not in st.session_state: st.session_state.reward_given = False

# ---------- LÓGICA DE RACHA ----------
def update_streak():
    today = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))
    last_date = str(progress["last_read_date"])
    
    if last_date == yesterday:
        progress["streak"] += 1
    elif last_date != today:
        progress["streak"] = 1
    
    progress["last_read_date"] = today

# ---------- INTERFAZ ----------

def home():
    st.title(f"📚 ¡Hola, {progress['name']}!")
    c1, c2 = st.columns(2)
    c1.metric("💰 EdiCoins", progress['points'])
    c2.metric("🔥 Racha", f"{progress['streak']} días")

    st.subheader("Elige una historia para leer:")
    for story in stories:
        completada = story["id"] in progress["stories_completed"]
        icono = "✅" if completada else "📖"
        if st.button(f"{icono} {story['title']}", key=f"s_{story['id']}", use_container_width=True):
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
    if st.button("✨ ¡Ya terminé de leer!", use_container_width=True):
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
    
    opcion = st.radio("Selecciona tu respuesta:", q["options"], key=f"q_{idx}")

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
    puntos_obtenidos = 0
    
    st.title("¡Lectura Completada! 🎉")
    
    if not st.session_state.reward_given:
        # Solo damos puntos si es la primera vez que la lee
        if story["id"] not in progress["stories_completed"]:
            puntos_obtenidos = 10 + (st.session_state.score * 5)
            progress["points"] += puntos_obtenidos
            progress["stories_completed"].append(story["id"])
            update_streak()
            save_progress_to_sheets(progress)
            st.balloons()
            st.success(f"¡Has ganado {puntos_obtenidos} EdiCoins! Ya los guardé en tu cuenta.")
        else:
            st.info("¡Gracias por leerla de nuevo! Esta ya la tenías completada.")
        st.session_state.reward_given = True

    st.write(f"Aciertos: {st.session_state.score} de {len(story['questions'])}")
    if st.button("Volver al Inicio"):
        st.session_state.page = "home"
        st.rerun()

# ---------- NAVEGACIÓN PRINCIPAL ----------
if st.session_state.page == "home": home()
elif st.session_state.page == "reading": reading()
elif st.session_state.page == "quiz": quiz()
elif st.session_state.page == "result": result()

# Sidebar para el papá
with st.sidebar:
    st.divider()
    if st.checkbox("🔑 Modo Papá"):
        pass_input = st.text_input("Contraseña", type="password")
        if pass_input == "1234":
            st.write("### Estadísticas")
            st.write(f"Total respuestas: {progress['total_answers']}")
            st.write(f"Correctas: {progress['correct_answers']}")
            if st.button("🔄 Refrescar desde Google"):
                st.session_state.user_data = load_progress()
                st.rerun()
