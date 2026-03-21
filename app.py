import streamlit as st
from streamlit_gsheets import GSheetsConnection
from datetime import date, timedelta
from stories import stories
import pandas as pd

# ---------- CONFIGURACIÓN DE PÁGINA ----------
st.set_page_config(page_title="App de Lectura", layout="centered")

# ---------- CONEXIÓN A GOOGLE SHEETS ----------
def get_connection():
    try:
        # Limpieza automática de la llave privada (por si los Secrets tienen \n de más)
        secret_dict = st.secrets["connections"]["gsheets"].to_dict()
        if "\\n" in secret_dict["private_key"]:
            secret_dict["private_key"] = secret_dict["private_key"].replace("\\n", "\n")
        
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"Error en la configuración de Secrets: {e}")
        return None

conn = get_connection()

def load_progress():
    # Datos de respaldo por si falla la conexión
    default_data = {
        "name": "Lectora", "points": 0, "streak": 0, 
        "last_read_date": "2026-01-01", "stories_completed": [],
        "total_answers": 0, "correct_answers": 0
    }
    
    try:
        if conn is None: return default_data
        
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        # Intentamos leer la pestaña "Lectura_App"
        df = conn.read(spreadsheet=url, worksheet="Lectura_App", ttl=0)
        
        # Si la hoja no tiene filas de datos (solo títulos o vacía)
        if df is None or len(df) == 0:
            st.warning("⚠️ La Fila 2 del Excel está vacía. Usando datos nuevos.")
            return default_data
            
        # Tomamos la primera fila de datos
        raw_data = df.iloc[0].to_dict()
        
        # Limpiamos los datos para que Python no se confunda
        data = {
            "name": str(raw_data.get("name", "Lectora")),
            "points": int(raw_data.get("points", 0)) if not pd.isna(raw_data.get("points")) else 0,
            "streak": int(raw_data.get("streak", 0)) if not pd.isna(raw_data.get("streak")) else 0,
            "last_read_date": str(raw_data.get("last_read_date", "2026-01-01")),
            "total_answers": int(raw_data.get("total_answers", 0)) if not pd.isna(raw_data.get("total_answers")) else 0,
            "correct_answers": int(raw_data.get("correct_answers", 0)) if not pd.isna(raw_data.get("correct_answers")) else 0
        }
        
        # Procesar la lista de historias completadas (Celda E)
        stories_val = str(raw_data.get("stories_completed", ""))
        if stories_val.strip() in ["", "nan", "None"]:
            data["stories_completed"] = []
        else:
            # Convierte "1,2" en [1, 2]
            data["stories_completed"] = [int(i) for i in stories_val.split(",") if i.strip()]
            
        return data

    except Exception as e:
        st.error(f"Nota: No pude leer el Excel ({e}). Usando modo local.")
        return default_data

def save_progress_to_sheets(data):
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        # Convertimos la lista [1, 2] a texto "1,2" para Excel
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
        
        conn.update(spreadsheet=url, worksheet="Lectura_App", data=updated_df)
    except Exception as e:
        st.error(f"❌ Error al guardar en la nube: {e}")

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

# ---------- PÁGINAS ----------

def home():
    st.title(f"📚 ¡Hola, {progress['name']}!")
    c1, c2 = st.columns(2)
    c1.metric("💰 EdiCoins", progress['points'])
    c2.metric("🔥 Racha", f"{progress['streak']} días")

    st.subheader("Elige una historia:")
    opcion = st.radio("Respuesta:", q["options"], key=f"q_{idx}")

    if not st.session_state.answer_submitted:
        if st.button("Enviar"):
            st.session_state.answer_submitted = True
            st.rerun()
    else:
        if opcion == q["answer"]: st.success("¡Correcto! 🌟")
        else: st.error(f"Era: {q['answer']}")
        
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
    st.title("¡Resultados! 🎉")
    
    if not st.session_state.reward_given:
        if story["id"] not in progress["stories_completed"]:
            puntos = 10 + (st.session_state.score * 5)
            progress["points"] += puntos
            progress["stories_completed"].append(story["id"])
            update_streak()
            save_progress_to_sheets(progress)
            st.balloons()
            st.success(f"¡Ganaste {puntos} EdiCoins!")
        else:
            st.info("¡Ya habías leído esta historia!")
        st.session_state.reward_given = True

    if st.button("Volver al Inicio"):
        st.session_state.page = "home"
        st.rerun()

# ---------- NAVEGACIÓN ----------
if st.session_state.page == "home": home()
elif st.session_state.page == "reading": reading()
elif st.session_state.page == "quiz": quiz()
elif st.session_state.page == "result": result()

# Sidebar Papá
with st.sidebar:
    if st.checkbox("🔑 Modo Papá"):
        if st.text_input("Pass", type="password") == "1234":
            if st.button("🔄 Forzar Recarga"):
                st.session_state.user_data = load_progress()
                st.rerun()
