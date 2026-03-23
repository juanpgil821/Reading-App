import streamlit as st
import random

# 1. Product List
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
    """Logic for the 300 EdiCoin Mystery Box probabilities"""
    roll = random.random() * 100  # 0 to 100
    
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

def show_market(progress, save_callback):
    st.title("🛍️ Edi-Mar-Ket")
    st.write(f"### Your Balance: {progress['points']} EdiCoins")
    st.write("---")

    # Display products in a grid (2 columns for mobile/compact view)
    cols = st.columns(2)
    
    for index, item in enumerate(PRODUCTS):
        with cols[index % 2]:
            st.markdown(f"### {item['icon']} {item['name']}")
            st.write(f"**Price:** {item['price']} EdiCoins")
            
            if st.button(f"Redeem {item['name']}", key=item['id']):
                if progress['points'] >= item['price']:
                    # Deduct points
                    progress['points'] -= item['price']
                    
                    # Special logic for Mystery Box
                    if item['id'] == "m3":
                        prize = open_mystery_box()
                        st.balloons()
                        st.info(f"🎁 THE MYSTERY BOX REVEALS... \n\n **{prize}**")
                        # Add to history if you want to track it later
                        st.warning("Take a screenshot and show it to Dad! 📸")
                    else:
                        st.balloons()
                        st.success(f"Successfully redeemed: {item['name']}! 🌟")
                        st.info("Show this screen to Dad to claim your prize! 📸")
                    
                    # Save the new point balance
                    save_callback(progress)
                else:
                    st.error("Not enough EdiCoins yet! Keep reading to earn more. 📚")

    st.write("---")
    st.write("💡 *Tip: Remember to take a screenshot of your purchase!*")

