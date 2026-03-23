import streamlit as st

# 1. DEFINICIÓN DE BADGES (Configuración)
# Añade aquí todos los que quieras en el futuro
BADGES = [
    {"id": "first_story", "name": "First Story", "icon": "📚", "req": "Completed 1st story", "type": "stories", "goal": 1},
    {"id": "on_fire", "name": "On Fire", "icon": "🔥", "req": "7 day streak", "type": "streak", "goal": 7},
    {"id": "genius", "name": "Genius", "icon": "🧠", "req": "100 correct answers", "type": "correct_answers", "goal": 100},
    {"id": "bookworm", "name": "Bookworm", "icon": "📖", "req": "50 stories completed", "type": "stories", "goal": 50},
    {"id": "legend", "name": "Legend", "icon": "💯", "req": "100 day streak", "type": "streak", "goal": 100},
    {"id": "immortal", "name": "Immortal", "icon": "👑", "req": "365 day streak", "type": "streak", "goal": 365},
]

def load_missions_css():
    st.markdown("""
        <style>
        .badge-card {
            padding: 15px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 10px;
            border: 2px solid #E0E0E0;
        }
        .badge-unlocked {
            background-color: #FFFACD; /* Dorado suave */
            border: 2px solid #FFD700;
            box-shadow: 0px 4px 10px rgba(255, 215, 0, 0.3);
        }
        .badge-locked {
            background-color: #F9F9F9;
            opacity: 0.6;
            filter: grayscale(100%);
        }
        .badge-icon { font-size: 40px; margin-bottom: 5px; }
        .badge-title { font-weight: bold; color: #4B0082; }
        .badge-req { font-size: 12px; color: #888; }
        </style>
    """, unsafe_allow_html=True)

def show_missions(progress):
    load_missions_css()
    st.title("🎖️ Royal Achievement Gallery")
    
    # Cálculos de progreso real
    stats = {
        "stories": len(progress.get("stories_completed", [])),
        "streak": progress.get("streak", 0),
        "correct_answers": progress.get("correct_answers", 0)
    }

    # Contador de badges
    unlocked_count = 0
    for b in BADGES:
        if stats[b["type"]] >= b["goal"]:
            unlocked_count += 1
            
    st.subheader(f"Unlocked: {unlocked_count} / {len(BADGES)} Badges")
    st.progress(unlocked_count / len(BADGES))
    st.write("---")

    # Mostrar Badges en rejilla (3 columnas)
    cols = st.columns(3)
    for index, b in enumerate(BADGES):
        is_unlocked = stats[b["type"]] >= b["goal"]
        status_class = "badge-unlocked" if is_unlocked else "badge-locked"
        lock_icon = "" if is_unlocked else "🔒 "
        
        with cols[index % 3]:
            st.markdown(f"""
                <div class="badge-card {status_class}">
                    <div class="badge-icon">{b['icon']}</div>
                    <div class="badge-title">{lock_icon}{b['name']}</div>
                    <div class="badge-req">{b['req']}</div>
                </div>
            """, unsafe_allow_html=True)

    if unlocked_count == len(BADGES):
        st.balloons()
        st.success("👑 AMAZING! You have collected ALL the royal badges!")

