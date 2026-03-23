import streamlit as st
import random

# ---------- 1. CONFIGURACIÓN VISUAL DE TARJETAS (CSS) ----------
# Este bloque de estilo unifica el diseño de cada producto
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

        /* Hacemos que el botón de Streamlit se adapte al contenedor */
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
    """Lógica para las probabilidades de la Mystery Box de 300 EdiCoins"""
    roll = random.random() * 100  # De 0 a 100
    
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
    # Cargamos el CSS específico para las tarjetas
    load_market_css()
    
    st.title("🛍️ Edi-Mar-Ket")
    st.write(f"### Your Balance: {progress['points']} EdiCoins")
    st.write("---")

    # Mostramos los productos en una cuadrícula de 2 columnas
    cols = st.columns(2)
    
    for index, item in enumerate(PRODUCTS):
        with cols[index % 2]:
            # --- INICIO DE LA TARJETA UNIFICADA (HTML/CSS) ---
            st.markdown(
                f"""
                <div class="product-card">
                    <div class="product-name">{item['icon']} {item['name']}</div>
                    <div class="product-price">Price: {item['price']} EdiCoins</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            # --- FIN DE LA TARJETA UNIFICADA ---
            
            # El botón de Streamlit se coloca justo debajo, pero el CSS lo estiliza
            # para que parezca parte del mismo grupo visual.
            if st.button(f"Redeem", key=item['id']):
                if progress['points'] >= item['price']:
                    # Descontar puntos
                    progress['points'] -= item['price']
                    
                    # Lógica especial para la Mystery Box
                    if item['id'] == "m3":
                        prize = open_mystery_box()
                        st.balloons()
                        st.info(f"🎁 THE MYSTERY BOX REVEALS... \n\n **{prize}**")
                        st.warning("Take a screenshot and show it to Dad! 📸")
                    else:
                        st.balloons()
                        st.success(f"Successfully redeemed: {item['name']}! 🌟")
                        st.info("Show this screen to Dad to claim your prize! 📸")
                    
                    # Guardar el nuevo balance de puntos
                    save_callback(progress)
                    # Forzar recarga para actualizar el balance visual
                    st.rerun()
                else:
                    st.error("Not enough EdiCoins yet! Keep reading. 📚")

    st.write("---")
    st.write("💡 *Tip: Remember to take a screenshot of your purchase!*")

