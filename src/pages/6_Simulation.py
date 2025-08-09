import streamlit as st
from src.components import *
# from src.components

with open("static/css/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Titre principal
st.title("Analyse Projet d'Investissement Immobilier")

st.markdown("""
Bienvenue dans le simulateur d'investissement locatif.  
Vous pouvez ici renseigner toutes les dimensions de votre projet, des coûts initiaux à la fiscalité, en passant par les loyers, les prêts, les travaux, etc.  
À la fin, vous pouvez télécharger un récapitulatif **complet en CSV** ou **générer un rapport PDF**.
""")

st.markdown("")
st.markdown("")

Bien.render()
Pret.render()
Loyer.render()
Travaux.render()
Frais.render()
Marche.render()
Hypothese.render()

if st.button("Compute"):
    Result.render()


