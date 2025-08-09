import streamlit as st
from dateutil.relativedelta import relativedelta

from src.utils.data_store import DataStore 

class Marche:
    
    @staticmethod
    def render():
        with st.expander("6️⃣ Caractéristiques du Marché Immobilier – *Cliquez pour ouvrir*", expanded=False):

            st.subheader("Données Quantitatives du Marché")
            st.divider()

            # Prix moyen au m²
            st.markdown("### Prix moyen au m² (€)")
            prix_m2 = st.number_input("Prix moyen au m² (€)", min_value=0, max_value=20000, value=3000, step=100, key="prix_m2")

            # Taux de croissance des prix
            st.markdown("### Taux de croissance des prix immobilier (%)")
            croissance_prix = st.number_input("Taux de Croissance des Prix (%)", min_value=-10.0, max_value=10.0, value=2.0, step=0.1, key="croissance_prix")

            # Loyer moyen au m²
            st.markdown("### Loyer moyen au m² (€)")
            loyer_m2 = st.number_input("Loyer moyen au m² (€)", min_value=0, max_value=500, value=15, step=1, key="loyer_m2")

            # Rendement locatif brut
            st.markdown("### Rendement Locatif Brut (%)")
            rendement_locatif = st.number_input("Rendement Locatif Brut (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.1, key="rendement_locatif")

            # Taux de vacance locative
            st.markdown("### Taux de Vacance Locative (%)")
            vacance_locative = st.number_input("Taux de Vacance Locative (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5, key="vacance_locative")

            # Durée moyenne de vente
            st.markdown("### Durée Moyenne de Vente (jours)")
            duree_vente = st.number_input("Durée Moyenne de Vente (jours)", min_value=0, max_value=1000, value=90, step=10, key="duree_vente")

            # Population
            st.markdown("### Population de la Ville")
            population = st.number_input("Population", min_value=0, max_value=10000000, value=100000, step=1000, key="population")

            # Revenu médian
            st.markdown("### Revenu Médian des Ménages (€)")
            revenu_median = st.number_input("Revenu Médian (€)", min_value=0, max_value=100000, value=30000, step=500, key="revenu_median")

            st.subheader("Données Qualitatives du Marché")
            st.divider()

            # Typologie de la demande
            st.markdown("### Typologie de la Demande")
            typologie_demande = st.selectbox("Typologie principale", 
                                             options=["Familles", "Étudiants", "Jeunes actifs", "Retraités", "Mixte"],
                                             key="typologie_demande")

            # Qualité des infrastructures
            st.markdown("### Qualité des Infrastructures")
            infrastructures = st.select_slider("Qualité des infrastructures", options=["Faible", "Moyenne", "Bonne", "Excellente"], key="infrastructures")

            # Attractivité économique
            st.markdown("### Attractivité Économique")
            attractivite_economique = st.select_slider("Attractivité économique", options=["Faible", "Moyenne", "Forte"], key="attractivite_economique")

            # Risques spécifiques
            st.markdown("### Risques Spécifiques")
            risques = st.multiselect("Risques présents", 
                                     options=["Inondation", "Séisme", "Montée des eaux", "Pollution", "Aucun"], 
                                     key="risques_specifiques")

            # Projets urbains
            st.markdown("### Projets Urbains en cours")
            projets_urbains = st.text_area("Décrire les projets urbains majeurs", key="projets_urbains")

            # Pression réglementaire
            st.markdown("### Pression Réglementaire")
            pression_reglementaire = st.selectbox("Niveau de pression réglementaire", 
                                                  options=["Faible", "Moyenne", "Forte"], 
                                                  key="pression_reglementaire")

            
            DataStore.set("marche", {
                "prix_m2": prix_m2,
                "croissance_prix": croissance_prix,
                "loyer_m2": loyer_m2,
                "rendement_locatif": rendement_locatif,
                "vacance_locative": vacance_locative,
                "duree_vente": duree_vente,
                "population": population,
                "revenu_median": revenu_median,
                "typologie_demande": typologie_demande,
                "infrastructures": infrastructures,
                "attractivite_economique": attractivite_economique,
                "risques_specifiques": risques,
                "projets_urbains": projets_urbains,
                "pression_reglementaire": pression_reglementaire
            })