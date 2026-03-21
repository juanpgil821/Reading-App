import streamlit as st
import json
from stories import get_story  # tu función para obtener historias

# --------------------------
# 1️⃣ Cargar progreso
# --------------------------
try:
    with open("progress.json", "r") as f:
        progress = json.load(f)
except FileNotFoundError:
    progress = {}

user_name = "Edimar"
# Inicializar si no existe
if user_name not in progress:
    progress[user_name] = {"edicoins": 0, "completed_stories": []}
elif "edicoins" not in progress[user_name]:
    progress[user_name]["edicoins"] = 0
elif "completed_stories" not in progress[user_name]:
    progress[user_name]["completed_stories"] = []

user_coins = progress[user_name]["edicoins"]

# --------------------------
# 2️⃣ Mostrar contador de Edicoins
# --------------------------
st.write(f"🪙 Edicoins: {user_coins}")

# --------------------------
# 3️⃣ Selección o carga de historia
# --------------------------
# Por simplicidad, tomamos story_1 como ejemplo
story = get_story("story_1")  # debe devolver dict con keys: text, questions, id
st.write(story["text"])

# --------------------------
# 4️⃣ Mostrar preguntas y recibir respuestas
# --------------------------
correct_answers = 0
for q in story["questions"]:
    answer = st.text_input(q["question"], key=q["question"])
    if st.button(f"Submit answer for '{q['question']}'", key=f"btn_{q['question']}"):
        if answer.strip().lower() == q["answer"]:
            st.success("Correct!")
            correct_answers += 1
        else:
            st.error("Try again!")

# --------------------------
# 5️⃣ Dar Edicoins si todas correctas
# --------------------------
if correct_answers == len(story["questions"]):
    if story["id"] not in progress[user_name]["completed_stories"]:
        # Agregar historia completada
        progress[user_name]["completed_stories"].append(story["id"])
        # Sumar Edicoins
        progress[user_name]["edicoins"] += 3  # por historia completada
        user_coins = progress[user_name]["edicoins"]
        st.balloons()  # 🎉 pequeño efecto de celebración
        st.success(f"You earned 3 Edicoins! Total: {user_coins} 🪙")

        # Guardar progreso
        with open("progress.json", "w") as f:
            json.dump(progress, f, indent=4)
