import streamlit as st

# 1. DEFINICIÓN DE LA JERARQUÍA REAL
# Los puntos son ACUMULADOS (Lifetime), no el balance actual.
LEVELS = [
    {"level": 1, "name": "Peasant", "min_pts": 0, "icon": "🧸", "bonus": "+20 EdiCoins", "desc": "The journey begins..."},
    {"level": 2, "name": "Villager", "min_pts": 300, "icon": "🪵", "bonus": "+50 EdiCoins", "desc": "You are now part of the Kingdom!"},
    {"level": 3, "name": "Castle Helper", "min_pts": 800, "icon": "🏰", "bonus": "Free Mystery Box", "desc": "Welcome inside the castle walls!"},
    {"level": 4, "name": "Maid", "min_pts": 1500, "icon": "🧹", "bonus": "+100 EdiCoins", "desc": "A trusted member of the royal staff."},
    {"level": 5, "name": "Lady", "min_pts": 2500, "icon": "🎀", "bonus": "+100 EdiCoins", "desc": "You are gaining high status!"},
    {"level": 6, "name": "Duchess", "min_pts": 4000, "icon": "💍", "bonus": "Better Mystery Box Odds", "desc": "Member of the High Nobility."},
    {"level": 7, "name": "Princess", "min_pts": 6000, "icon": "👑", "bonus": "5% Shop Discount", "desc": "A central figure of the Realm."},
    {"level": 8, "name": "Queen", "min_pts": 9000, "icon": "💎", "bonus": "10% Shop Discount", "desc": "Total control of the Kingdom!"},
    {"level": 9, "name": "Empress", "min_pts": 15000, "icon": "🌟", "bonus": "20% Shop Discount", "desc": "Legendary Ruler of the Empire!"},
]

def get_current_level(total_points):
    """Calcula en qué nivel está basado en puntos totales"""
    current = LEVELS[0]
    for l in LEVELS:
        if total_points >= l['min_pts']:
            current = l
        else:
            break
    return current

def get_next_level(total_points):
    """Calcula el siguiente nivel y cuánto falta"""
    for l in LEVELS:
        if l['min_pts'] > total_points:
            return l
    return None # Nivel máximo alcanzado

def show_level_ui(progress):
    """Muestra el progreso de nivel en el Sidebar o Home"""
    # Usamos 'total_points_earned' para que no baje de nivel al gastar
    total_pts = progress.get("total_points_earned", 0)
    current = get_current_level(total_pts)
    next_lvl = get_next_level(total_pts)

    st.markdown(f"""
        <div style="background-color: rgba(255, 255, 255, 0.8); padding: 10px; border-radius: 15px; border: 2px solid #FFD700; text-align: center;">
            <p style="margin: 0; font-size: 14px; color: #4B0082;">Royal Rank</p>
            <h2 style="margin: 0;">{current['icon']} {current['name']}</h2>
        </div>
    """, unsafe_allow_html=True)

    if next_lvl:
        pts_needed = next_lvl['min_pts'] - total_pts
        progress_pct = min(1.0, total_pts / next_lvl['min_pts'])
        st.write(f"Next Rank: **{next_lvl['name']}** (in {pts_needed} pts)")
        st.progress(progress_pct)

def check_level_up(progress):
    """Lógica para detectar si acaba de subir de nivel y dar premios"""
    # Esta función se llamaría en app.py después de ganar puntos
    total_pts = progress.get("total_points_earned", 0)
    # Aquí podrías guardar el 'last_level_seen' en el JSON para disparar la animación solo una vez
    pass

