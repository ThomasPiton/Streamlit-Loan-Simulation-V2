import streamlit as st

pages = {
    # 1. put Home first
    # "Home": [
    #     st.Page("src/pages/2_Home.py", title="Home", icon=":material/home:")
    # ],

    "Simulations": [
        st.Page("src/pages/6_Simulation.py", title="Simulation", icon=":material/monitoring:")
    ],
    
    "Others": [
        st.Page("src/pages/3_About.py", title="About", icon=":material/info:"),
        st.Page("src/pages/1_FAQ.py",   title="FAQ",   icon=":material/help:"),
        st.Page("src/pages/4_Contact.py", title="Contact", icon=":material/contacts_product:"),
    ],
}

pg = st.navigation(pages)

# 3. optional: your logo
st.logo("./static/img/bank_logo.png", icon_image="./static/img/bank_logo.png")

# 4. finally run
pg.run()