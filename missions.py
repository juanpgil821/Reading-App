import streamlit as st
from datetime import date

# ---------- 1. DEFINICIÓN DE BADGES (Configuración) ----------
BADGES = [
    # --- STORIES ---
    {"id": "first_story", "name": "First Step", "icon": "🌱", "req": "Completed 1st story", "type": "stories", "goal": 1},
    {"id": "small_library", "name": "Small Library", "icon": "📚", "req": "10 stories completed", "type": "stories", "goal": 10},
    {"id": "speed_reader", "name": "Speed Reader", "icon": "⚡", "req": "5 stories in one day!", "type": "daily_goal", "goal": 0},
    {"id": "avid_reader", "name": "Avid Reader", "icon": "📖", "req": "25 stories completed", "type": "stories", "goal": 25},
    {"id": "bookworm", "name": "Bookworm", "icon": "📙", "req": "50 stories completed", "type": "stories", "goal": 50},
    {"id": "master_reader", "name": "Master Reader", "icon": "🏰", "req": "100 stories completed", "type": "stories", "goal": 100},
    # --- STREAKS (Rachas) ---
    {"id": "starting_up", "name": "Consistent", "icon": "✨", "req": "7 day streak", "type": "streak", "goal": 7},
    {"id": "on_fire", "name": "On Fire", "icon": "🔥", "req": "15 day streak", "type": "streak", "goal": 15},
    {"id": "half_month", "name": "Bronze Medal", "icon": "🥉", "req": "30 day streak", "type": "streak", "goal": 30},
    {"id": "full_month", "name": "Silver Medal", "icon": "🥈", "req": "60 day streak", "type": "streak", "goal": 60},
    {"id": "golden_streak", "name": "Golden Rarity", "icon": "🥇", "req": "100 day streak", "type": "streak", "goal": 100},
    {"id": "legend", "name": "Legend", "icon": "💯", "req": "200 day streak", "type": "streak", "goal": 200},
    {"id": "immortal", "name": "Immortal", "icon": "👑", "req": "365 day streak", "type": "streak", "goal": 365},
    # --- ACCURACY (Preguntas Correctas) ---
    {"id": "smart_start", "name": "Smart Start", "icon": "💡", "req": "50 correct answers", "type": "correct_answers", "goal": 50},
    {"id": "thinker", "name": "Deep Thinker", "icon": "🔍", "req": "100 correct answers", "type": "correct_answers", "goal": 100},
    {"id": "genius", "name": "Genius", "icon": "🧠", "req": "250 correct answers", "type": "correct_answers", "goal": 250},
    {"id": "oracle", "name": "The Oracle", "icon": "🔮", "req": "500 correct answers", "type": "correct_answers", "goal": 500},
    {"id": "sage", "name": "Royal Sage", "icon": "🎓", "req": "1000 correct answers", "type": "correct_answers", "goal": 1000},
]

def load_missions_css():
    st.markdown("""
        <style>
        .badge-card {
            padding: 15px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 15px;
            border: 2px solid #E0E0E0;
            min-height: 150px;
            transition: 0.3s;
        }
        .badge-unlocked {
            background-color: #FFFACD;
            border: 2px solid #FFD700;
            box-shadow: 0px 4px 10px rgba(255, 215, 0, 0.3);
        }
        .badge-locked {
            background-color: #F9F9F9;
            opacity: 0.5;
            filter: grayscale(80%);
        }
        .badge-icon { font-size: 45px; margin-bottom: 5px; }
        .badge-title { font-weight: bold; color: #4B0082; font-size: 15px; }
        .badge-req { font-size: 12px; color: #888; margin-top: 5px; }
        </style>
    """, unsafe_allow_html=True)

def show_missions(progress):
    load_missions_css()
    st.title("🎖️ Royal Achievement Gallery")
    today_str = str(date.today())
    stories_today = progress.get("daily_reads", {}).get(today_str, 0)
    stats = {
        "stories": len(progress.get("stories_completed", [])),
        "streak": progress.get("streak", 0),
        "correct_answers": progress.get("correct_answers", 0),
        "daily_goal": stories_today 
    }
    unlocked_count = 0
    for b in BADGES:
        if stats[b["type"]] >= b["goal"]:
            unlocked_count += 1
    st.subheader(f"Unlocked: {unlocked_count} / {len(BADGES)} Badges")
    st.progress(unlocked_count / len(BADGES))
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
        st.success("👑 LEGENDARY! You have conquered the entire kingdom!")

