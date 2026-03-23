import streamlit as st
import random
import time

# ---------- 1. CONFIGURACIÓN VISUAL (CSS IGUAL AL ANTERIOR) ----------
def load_market_css():
    st.markdown(
        """
        <style>
        .product-card {
            background-color: rgba(255, 255, 255, 0.9);
            border: 2px solid #FFB6C1;
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 15px;
            text-align: center;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            min-height: 150px;
        }
        .product-name { color: #4B0082; font-size: 20px; font-weight: bold; margin-bottom: 5px; }
        .product-price { color: #FF1493; font-size: 16px; margin-bottom: 10px; }
        div.stButton > button { width: auto !important; padding: 5px 20px !important; font-size: 16px !important; margin: 0 auto !important; display: block !important; }
        
        /* Animación de parpadeo para la ruleta */
        .slot-machine {
            font-size: 30px;
            font-weight: bold;
            color: #FF1493;
            text-align: center;
            padding: 20px;
            border: 4px dashed #FFD700;
            border-radius: 20px;
            background: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# ---------- 2. LISTA DE PRODUCTOS ----------
PRODUCTS = [
    {"id": "m1", "name": "20min Xtra-Screen", "price": 100, "icon": "📱"},
    {"id": "m0", "name": "Streak Saver 🛡️", "price": 200, "icon": "🛡️"},
    {"id": "m2", "name": "1 hr Xtra-Screen", "price": 200, "icon": "⏳"},
    {"id": "m3", "name": "Mystery Box 🎁", "price": 300, "icon": "❓"},
    {"id": "m4", "name": "Choose Meal/Rest.", "price": 400, "icon": "🍕"},
    {"id": "m5", "name": "Robux / Cash", "price": 600, "icon": "💸"},
    {"id": "m6", "name": "No-Limit Screen Night", "price": 700, "icon": "🌙"},
    {"id": "m7", "name": "Invite Friends Over", "price": 750, "icon": "👭"},
    {"id": "m8", "name": "Cinema Night", "price": 800, "icon": "🎬"},
    {"id": "m9", "name": "Mini Golf / Bowling", "price": 1000, "icon": "🎳"},
    {"id": "m10", "name": "Park Day Adventure", "price": 1200, "icon": "🌳"},
]

# ---------- 3. LÓGICA DE EVENTO MYSTERY BOX ----------
def run_mystery_animation():
    placeholder = st.empty()
    possible_prizes = [
        "1 hr Xtra-Screen ⏳", "Robux! 💸", "Cinema Night 🎬", 
        "Mini Golf 🎳", "No-Limit Screen 🌙", "Mystery Item 🎁"
    ]
    
    # Simulación de ruleta girando
    for i in range(15):
        prize_sample = random.choice(possible_prizes)
        placeholder.markdown(f'<div class="slot-machine">🎲 Rolling: {prize_sample}</div>', unsafe_allow_html=True)
        time.sleep(0.1 + (i * 0.02)) # Se va volviendo más lenta
    
    # Resultado final basado en probabilidades reales
    roll = random.random() * 100
    if roll < 50:
        final = "1 hr Xtra-Screen! ⏳"
        almost = "Robux! 💸"
    elif roll < 75:
        final = "Robux! 💸"
        almost = "No-Limit Screen Night! 🌙"
    elif roll < 90:
        final = "No-Limit Screen Night! 🌙"
        almost = "Cinema Night! 🎬"
    elif roll < 98:
        final = "Cinema Night! 🎬"
        almost = "Mini Golf / Bowling! 🎳"
    else:
        final = "Mini Golf / Bowling! 🎳"
        almost = "A Magic Wand! ✨"

    placeholder.empty()
    return final, almost

# ---------- 4. FUNCIÓN PRINCIPAL ----------
def show_market(progress, save_callback):
    load_market_css()
    st.title("🛍️ Edi-Mar-Ket")
    st.write(f"### Your Balance: {progress['points']} EdiCoins")
    
    savers = progress.get("streak_saver", 0)
    if savers > 0:
        st.write(f"🛡️ **Protective Shields Active:** {savers}")
        
    st.write("---")
    cols = st.columns(2)
    
    for index, item in enumerate(PRODUCTS):
        with cols[index % 2]:
            st.markdown(f'<div class="product-card"><div class="product-name">{item["icon"]} {item["name"]}</div><div class="product-price">Price: {item["price"]} EdiCoins</div></div>', unsafe_allow_html=True)
            
            if st.button(f"Redeem", key=item['id']):
                if progress['points'] >= item['price']:
                    progress['points'] -= item['price']
                    
                    if item['id'] == "m3":
                        # --- EFECTO EVENTO CAJA MISTERIOSA ---
                        prize, almost_prize = run_mystery_animation()
                        st.balloons()
                        st.markdown(f"""
                            <div style="text-align: center; background: #FFD700; padding: 20px; border-radius: 15px; border: 5px solid #FF1493;">
                                <h2 style="color: #4B0082;">🎉 YOU WON:</h2>
                                <h1 style="color: #FF1493;">{prize}</h1>
                                <p style="color: #4B0082; font-weight: bold; margin-top: 10px; border-top: 1px solid rgba(0,0,0,0.1); padding-top: 10px;">
                                    😲 SO CLOSE! You almost won: {almost_prize}
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                        st.warning("Take a screenshot for Dad! 📸")
                    
                    elif item['id'] == "m0":
                        progress["streak_saver"] = progress.get("streak_saver", 0) + 1
                        st.balloons()
                        st.success("🛡️ Streak Saver purchased!")
                    else:
                        st.balloons()
                        st.success(f"Successfully redeemed: {item['name']}! 🌟")
                    
                    save_callback(progress)
                    # No hacemos rerun inmediato para que pueda ver la animación del premio
                else:
                    st.error("Not enough EdiCoins yet! Keep reading. 📚")
