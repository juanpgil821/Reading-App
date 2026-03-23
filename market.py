import streamlit as st
import random

# ---------- 1. CONFIGURACIÓN VISUAL DE TARJETAS (CSS) ----------
def load_market_css():
    st.markdown(
        """
        <style>
        /* Estilo para la tarjeta del producto */
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
        
        /* Estilo para el icono y nombre del premio */
        .product-name {
            color: #4B0082;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        /* Estilo para el precio */
        .product-price {
            color: #FF1493;
            font-size: 16px;
            margin-bottom: 10px;
        }

        /* Botón adaptado */
        div.stButton > button {
            width: auto !important;
            padding: 5px 20px !important;
            font-size: 16px !important;
            margin: 0 auto !important;
            display: block !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# ---------- 2. LISTA DE PRODUCTOS ----------
PRODUCTS = [
    {"id": "m1", "name": "20min Xtra-Screen", "price": 100, "icon": "📱"},
    {"id": "m0", "name": "Streak Saver 🛡️", "price": 200, "icon": "🛡️"}, # Nuevo objeto
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

def open_mystery_box():
    """Lógica para las probabilidades de la Mystery Box"""
    roll = random.random() * 100
    if roll < 50:
        return "1 hr Xtra-Screen! ⏳"
    elif roll < 75:
        return "Robux! 💸"
    elif roll < 90:
        return "No-Limit Screen Night! 🌙"
    elif roll < 98:
        return "Cinema Night! 🎬"
    else:
        return "Mini Golf / Bowling! 🎳"

# ---------- 3. FUNCIÓN PRINCIPAL DE LA TIENDA ----------
def show_market(progress, save_callback):
    load_market_css()
    
    st.title("🛍️ Edi-Mar-Ket")
    st.write(f"### Your Balance: {progress['points']} EdiCoins")
    
    # Mostrar escudos actuales si tiene
    savers = progress.get("streak_saver", 0)
    if savers > 0:
        st.write(f"🛡️ **Protective Shields Active:** {savers}")
        
    st.write("---")

    cols = st.columns(2)
    
    for index, item in enumerate(PRODUCTS):
        with cols[index % 2]:
            st.markdown(
                f"""
                <div class="product-card">
                    <div class="product-name">{item['icon']} {item['name']}</div>
                    <div class="product-price">Price: {item['price']} EdiCoins</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            if st.button(f"Redeem", key=item['id']):
                if progress['points'] >= item['price']:
                    # Descontar puntos
                    progress['points'] -= item['price']
                    
                    # Lógica según el objeto
                    if item['id'] == "m3":
                        prize = open_mystery_box()
                        st.balloons()
                        st.info(f"🎁 THE MYSTERY BOX REVEALS... \n\n **{prize}**")
                        st.warning("Take a screenshot and show it to Dad! 📸")
                    
                    elif item['id'] == "m0":
                        # Lógica del Streak Saver
                        progress["streak_saver"] = progress.get("streak_saver", 0) + 1
                        st.balloons()
                        st.success("🛡️ Streak Saver purchased! Your progress is now safer.")
                    
                    else:
                        st.balloons()
                        st.success(f"Successfully redeemed: {item['name']}! 🌟")
                        st.info("Show this screen to Dad to claim your prize! 📸")
                    
                    # Guardar cambios
                    save_callback(progress)
                    st.rerun()
                else:
                    st.error("Not enough EdiCoins yet! Keep reading. 📚")

    st.write("---")
    st.write("💡 *Tip: The Streak Saver 🛡️ prevents your streak from resetting to 0 if you miss a day.*")

