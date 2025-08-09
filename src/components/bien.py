import streamlit as st
from dateutil.relativedelta import relativedelta

from src.utils.data_store import DataStore 
from src.components.config import TYPE_BIEN,STRATEGIES, ZONE_BIEN

class Bien:
    
    @staticmethod
    def render():
        with st.expander("1️⃣ Caractéristiques du Bien Immobilier – *Cliquez pour ouvrir*", expanded=False): 
            
            st.subheader("Informations sur le bien")
            st.divider()
            
            type_bien = st.selectbox("Type de bien", TYPE_BIEN, key="type_bien")
            selected_strategy = st.selectbox("Choisissez une stratégie d’investissement immobilier :", list(STRATEGIES.keys()), key="strategie_invest")
            st.markdown(f"**Description :** {STRATEGIES[selected_strategy]}")

            prix_achat = st.number_input("Prix du bien (€)", min_value=0, value=100000, step=1, key="prix_achat")
            surface = st.number_input("Surface habitable (m²)", min_value=0.0, step=1.0,value=50.0, key="surface")
            surface_annexe = st.number_input("Surface annexe (balcon, cave, garage) (m²)", min_value=0.0, step=1.0, key="surface_annexe")
            
            # Option Surface Avancée
            surface_avancee = st.checkbox("Afficher les surfaces avancées", key="surface_avancee")
            
            if surface_avancee:
                surface_terrasse = st.number_input("Surface terrasse (m²)", min_value=0.0, step=1.0, key="surface_terrasse")
                surface_balcon = st.number_input("Surface balcon (m²)", min_value=0.0, step=1.0, key="surface_balcon")
                surface_loggia = st.number_input("Surface loggia (m²)", min_value=0.0, step=1.0, key="surface_loggia")
                surface_veranda = st.number_input("Surface véranda (m²)", min_value=0.0, step=1.0, key="surface_veranda")
                surface_cave = st.number_input("Surface cave (m²)", min_value=0.0, step=1.0, key="surface_cave")
                surface_grenier = st.number_input("Surface grenier (m²)", min_value=0.0, step=1.0, key="surface_grenier")
                surface_parking = st.number_input("Surface parking/garage (m²)", min_value=0.0, step=1.0, key="surface_parking")
                surface_jardin = st.number_input("Surface jardin privatif (m²)", min_value=0.0, step=1.0, key="surface_jardin")
                surface_combles = st.number_input("Surface combles aménageables (m²)", min_value=0.0, step=1.0, key="surface_combles")
                surface_extension = st.number_input("Surface extension prévue (m²)", min_value=0.0, step=1.0, key="surface_extension")
                surface_perdue = st.number_input("Surface perdue (m²)", min_value=0.0, step=1.0, key="surface_perdue")
            else:
                # Valeurs par défaut pour ne pas planter DataStore
                surface_terrasse = surface_balcon = surface_loggia = surface_veranda = 0.0
                surface_cave = surface_grenier = surface_parking = surface_jardin = 0.0
                surface_combles = surface_extension = surface_perdue = 0.0

            nb_pieces = st.number_input("Nombre de pièces", min_value=0, step=1, key="nb_pieces")
            nb_chambres = st.number_input("Nombre de chambres", min_value=0, step=1, key="nb_chambres")
            annee_construction = st.number_input("Année de construction", min_value=1800, max_value=2100, step=1, key="annee_construction")
            etage = st.number_input("Étage", min_value=0, step=1, key="etage")
            ascenseur = st.checkbox("Ascenseur", key="ascenseur")
            etat_general = st.selectbox("État général du bien", ["Neuf", "Rénové", "Bon état", "Travaux à prévoir"], key="etat_general")
            date_horizon = st.selectbox("Période d'investissement (année)", [1,5,10,15,20,25,30,35,40,45,50], key="date_horizon")
            dpe = st.selectbox("Classe énergétique (DPE)", ["A", "B", "C", "D", "E", "F", "G"], key="dpe")
            localisation = st.text_input("Localisation (ville, quartier, code postal)", key="localisation")
            zone_loyers = st.selectbox("Zone géographique (loyers réglementés)", ZONE_BIEN, key="zone_loyers")
            situation_locative = st.selectbox("Situation locative actuelle", ["Libre", "Loué", "Bail en cours", "Résidence principale"], key="situation_locative")
            meuble = st.selectbox("Meublé ou non meublé", ["Meublé", "Non meublé"], key="meuble")

            DataStore.set("bien", {
                "type_bien": type_bien,
                "strategy": selected_strategy,
                "prix_achat": prix_achat,
                "surface": surface,
                "surface_annexe": surface_annexe,
                "surface_terrasse": surface_terrasse,
                "surface_balcon": surface_balcon,
                "surface_loggia": surface_loggia,
                "surface_veranda": surface_veranda,
                "surface_cave": surface_cave,
                "surface_grenier": surface_grenier,
                "surface_parking": surface_parking,
                "surface_jardin": surface_jardin,
                "surface_combles": surface_combles,
                "surface_extension": surface_extension,
                "surface_perdue": surface_perdue,
                "date_horizon": date_horizon,
                "nb_pieces": nb_pieces,
                "nb_chambres": nb_chambres,
                "annee_construction": annee_construction,
                "etage": etage,
                "ascenseur": ascenseur,
                "etat_general": etat_general,
                "dpe": dpe,
                "localisation": localisation,
                "zone_loyers": zone_loyers,
                "situation_locative": situation_locative,
                "meuble": meuble
            })