import streamlit as st

# 1. DEFINICIÓN EXACTA DE TU JERARQUÍA REAL
LEVELS = [
    {"level": 1, "name": "Peasant", "min_pts": 0, "icon": "🧸", "bonus_coins": 20, "desc": "Inicio del viaje", "reward_text": "+20 EdiCoins"},
    {"level": 2, "name": "Villager", "min_pts": 300, "icon": "🪵", "bonus_coins": 50, "desc": "Ya formas parte del reino", "reward_text": "+50 EdiCoins"},
    {"level": 3, "name": "Castle Helper", "min_pts": 800, "icon": "🏰", "bonus_coins": 300, "desc": "Acceso a la vida dentro del castillo", "reward_text": "🎁 FREE Mystery Box!"},
    {"level": 4, "name": "Maid", "min_pts": 1500, "icon": "🧹", "bonus_coins": 100, "desc": "Mayor confianza en el castillo", "reward_text": "+100 EdiCoins"},
    {"level": 5, "name": "Lady", "min_pts": 2500, "icon": "🎀", "bonus_coins": 100, "desc": "Empieza a tener estatus", "reward_text": "+100 EdiCoins"},
    {"level": 6, "name": "Duchess", "min_pts": 4000, "icon": "💍", "bonus_coins": 0, "desc": "Alta nobleza", "reward_text": "✨ Mejores premios en Mystery Box"},
    {"level": 7, "name": "Princess", "min_pts": 6000, "icon": "👑", "bonus_coins": 0, "desc": "Figura central del reino", "reward_text": "🎟️ Cupón de descuento 5%"},
    {"level": 8, "name": "Queen", "min_pts": 9000, "icon": "💎", "bonus_coins": 0, "desc": "Control total del reino", "reward_text": "📜 Cupón de descuento 10%"},
    {"level": 9, "name": "Empress", "min_pts": 15000, "icon": "🌟", "bonus_coins": 0, "desc": "Nivel máximo / legendario", "reward_text": "👑 Cupón de descuento 20%"},
]

def get_current_level(total_points):
    current = LEVELS[0]
    for l in LEVELS:
        if total_points >= l['min_pts']:
            current = l
        else:
            break
    return current

def get_next_level(total_points):
    for l in LEVELS:
        if l['min_pts'] > total_points:
            return l
    return None

def show_level_ui(progress):
    total_pts = progress.get("total_points_earned", 0)
    current = get_current_level(total_pts)
    next_lvl = get_next_level(total_pts)

    st.markdown(f"""
        <div style="background-color: rgba(255, 255, 255, 0.9); padding: 15px; border-radius: 20px; border: 3px solid #FFD700; text-align: center; margin-bottom: 20px;">
            <p style="margin: 0; font-size: 14px; color: #4B0082; font-weight: bold;">Rango Real Actual</p>
            <h1 style="margin: 5px 0; font-size: 45px;">{current['icon']}</h1>
            <h2 style="margin: 0; color: #FF1493;">{current['name']}</h2>
            <p style="font-style: italic; color: #666; font-size: 14px;">"{current['desc']}"</p>
        </div>
    """, unsafe_allow_html=True)

    if next_lvl:
        pts_needed = next_lvl['min_pts'] - total_pts
        current_range = next_lvl['min_pts'] - current['min_pts']
        current_progress = total_pts - current['min_pts']
        pct = min(1.0, current_progress / current_range)
        
        st.write(f"Próximo Rango: **{next_lvl['name']}**")
        st.progress(pct)
        st.write(f" ✨ *¡Faltan {pts_needed} puntos para tu próximo título!*")

def check_level_up(progress):
    total_pts = progress.get("total_points_earned", 0)
    current = get_current_level(total_pts)
    last_lvl = progress.get("last_level_seen", 1)
    
    if current['level'] > last_lvl:
        # Dar bono de monedas si aplica (para niveles 1, 2, 3, 4, 5)
        bonus = current['bonus_coins']
        progress['points'] += bonus
        progress['last_level_seen'] = current['level']
        
        st.balloons()
        st.markdown(f"""
            <div style="background-color: #FFD700; padding: 25px; border-radius: 20px; text-align: center; border: 5px solid #FF1493; margin: 20px 0;">
                <h1 style="color: #4B0082;">🎉 ¡ASCENSO REAL! 🎉</h1>
                <h2 style="color: white; text-shadow: 2px 2px #FF1493;">¡Ahora eres {current['name']}!</h2>
                <p style="font-size: 18px; color: #4B0082;">El reino celebra tu sabiduría y esfuerzo.</p>
                <div style="font-size: 24px; font-weight: bold; background: white; border-radius: 10px; padding: 10px; display: inline-block;">
                    🎁 Premio: {current['reward_text']}
                </div>
            </div>
        """, unsafe_allow_html=True)
        return True
    return False

