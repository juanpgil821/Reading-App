import streamlit as st

# 1. EXACT ROYAL HIERARCHY DEFINITION (English Version)
LEVELS = [
    {"level": 1, "name": "Peasant", "min_pts": 0, "icon": "🧸", "bonus_coins": 20, "desc": "The journey begins...", "reward_text": "+20 EdiCoins"},
    {"level": 2, "name": "Villager", "min_pts": 300, "icon": "🪵", "bonus_coins": 50, "desc": "You are now part of the Kingdom!", "reward_text": "+50 EdiCoins"},
    {"level": 3, "name": "Castle Helper", "min_pts": 800, "icon": "🏰", "bonus_coins": 300, "desc": "Access to life inside the castle", "reward_text": "🎁 FREE Mystery Box!"},
    {"level": 4, "name": "Maid", "min_pts": 1500, "icon": "🧹", "bonus_coins": 100, "desc": "Trusted member of the staff", "reward_text": "+100 EdiCoins"},
    {"level": 5, "name": "Lady", "min_pts": 2500, "icon": "🎀", "bonus_coins": 100, "desc": "You are gaining high status", "reward_text": "+100 EdiCoins"},
    {"level": 6, "name": "Duchess", "min_pts": 4000, "icon": "💍", "bonus_coins": 0, "desc": "High Nobility", "reward_text": "✨ Better prizes in Mystery Box"},
    {"level": 7, "name": "Princess", "min_pts": 6000, "icon": "👑", "bonus_coins": 0, "desc": "A central figure of the Realm", "reward_text": "🎟️ 5% Discount Coupon"},
    {"level": 8, "name": "Queen", "min_pts": 9000, "icon": "💎", "bonus_coins": 0, "desc": "Total control of the Kingdom", "reward_text": "📜 10% Discount Coupon"},
    {"level": 9, "name": "Empress", "min_pts": 15000, "icon": "🌟", "bonus_coins": 0, "desc": "Legendary / Maximum Level", "reward_text": "👑 20% Discount Coupon"},
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

    # UI principal del rango actual
    st.markdown(f"""
        <div style="background-color: rgba(255, 255, 255, 0.9); padding: 15px; border-radius: 20px; border: 3px solid #FFD700; text-align: center; margin-bottom: 20px;">
            <p style="margin: 0; font-size: 18px; color: #4B0082; font-weight: bold;">Current Royal Rank</p>
            <h1 style="margin: 5px 0; font-size: 60px;">{current['icon']}</h1>
            <h2 style="margin: 0; color: #FF1493; font-size: 32px;">{current['name']}</h2>
            <p style="font-style: italic; color: #666; font-size: 18px;">"{current['desc']}"</p>
        </div>
    """, unsafe_allow_html=True)

    # Barra de progreso al siguiente nivel
    if next_lvl:
        pts_needed = next_lvl['min_pts'] - total_pts
        current_range = next_lvl['min_pts'] - current['min_pts']
        current_progress = total_pts - current['min_pts']
        
        # Evitar división por cero si los niveles están mal configurados
        if current_range > 0:
            pct = min(1.0, current_progress / current_range)
        else:
            pct = 1.0
        
        st.write(f"### Next Rank: **{next_lvl['name']}**")
        st.progress(pct)
        st.write(f"✨ *Only **{pts_needed}** points to reach your next title!*")

def check_level_up(progress):
    """
    Checks if the user has reached a new level and awards the corresponding bonus.
    Uses 'last_level_seen' to ensure each reward is given only once.
    """
    total_pts = progress.get("total_points_earned", 0)
    current = get_current_level(total_pts)
    
    # Obtenemos el último nivel por el que cobró recompensa (default al nivel 1)
    last_lvl_num = progress.get("last_level_seen", 1)
    
    # Si el nivel actual es mayor al último nivel registrado como 'visto'
    if current['level'] > last_lvl_num:
        # 1. Entregar recompensa de monedas
        bonus = current.get('bonus_coins', 0)
        progress['points'] += bonus
        
        # 2. Actualizar el registro para evitar duplicados
        progress['last_level_seen'] = current['level']
        
        # 3. Mostrar la celebración visual
        st.balloons()
        st.markdown(f"""
            <div style="background-color: #FFD700; padding: 25px; border-radius: 20px; text-align: center; border: 5px solid #FF1493; margin: 20px 0;">
                <h1 style="color: #4B0082; font-size: 40px;">🎉 ROYAL ASCENSION! 🎉</h1>
                <h2 style="color: white; text-shadow: 2px 2px #FF1493; font-size: 35px;">You are now a {current['name']}!</h2>
                <p style="font-size: 22px; color: #4B0082;">The Kingdom celebrates your wisdom and effort.</p>
                <div style="font-size: 28px; font-weight: bold; background: white; border-radius: 10px; padding: 15px; display: inline-block; color: #FF1493; border: 2px solid #FF1493;">
                    🎁 Reward: {current['reward_text']}
                </div>
            </div>
        """, unsafe_allow_html=True)
        return True
        
    return False
