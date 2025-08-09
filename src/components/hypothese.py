import streamlit as st
from dateutil.relativedelta import relativedelta

from src.utils.data_store import DataStore 

class Hypothese:
    
    @staticmethod
    def render():
        with st.expander("7️⃣ Hypothèses de Croissance Économique et d'Inflation – *Cliquez pour ouvrir*", expanded=False):
            
            st.subheader("Hypothèses de Croissance et d'Inflation")
            st.divider()
            
            def input_with_frequency(label, key, default_value=0.0):
                col1, col2 = st.columns([2, 1])
                with col1:
                    taux = st.number_input(label, min_value=0.0, max_value=10.0, value=default_value, step=0.1, key=key)
                with col2:
                    frequence = st.selectbox("Fréquence de mise à jour", 
                                             options=["Annuelle", "Semestrielle", "Trimestrielle", "Mensuelle"],
                                             index=0, key=f"{key}_frequence")
                return taux, frequence

            data = {}

            # Taux de Croissance Économique Annuel
            st.markdown("### Taux de Croissance Économique Annuel (%)")
            st.markdown("Ce taux représente la croissance attendue de l'économie sur une année. Il est utilisé pour estimer la hausse des revenus, des prix et des autres éléments économiques.")
            data["taux_croissance_annuel"], data["frequence_taux_croissance_annuel"] = input_with_frequency("Taux de Croissance Économique Annuel (%)", "taux_croissance_annuel")

            # Taux d'Inflation Annuel
            st.markdown("### Taux d'Inflation Annuel (%)")
            st.markdown("L'inflation représente l'augmentation générale des prix dans l'économie, ce qui affecte les coûts des biens et services sur une période donnée.")
            data["taux_inflation"], data["frequence_taux_inflation"] = input_with_frequency("Taux d'Inflation Annuel (%)", "taux_inflation")

            # Taux d'Augmentation Annuel des Loyers
            st.markdown("### Taux d'Augmentation Annuel des Loyers (%)")
            st.markdown("Ce taux indique la hausse moyenne des loyers sur une année, en fonction de l'inflation et des conditions économiques du marché immobilier.")
            data["taux_augmentation_loyer"], data["frequence_taux_augmentation_loyer"] = input_with_frequency("Taux d'Augmentation Annuel des Loyers (%)", "taux_augmentation_loyer")
            
            # Croissance du Prix au M²
            st.markdown("### Croissance du Prix au M² (%)")
            st.markdown("Indique l'augmentation estimée du prix du mètre carré dans la région concernée.")
            data["taux_croissance_prix_m2"], data["frequence_taux_croissance_prix_m2"] = input_with_frequency("Croissance du Prix au M² (%)", "taux_croissance_prix_m2")

            # Croissance des Charges de Copropriété
            st.markdown("### Croissance des Charges de Copropriété (%)")
            st.markdown("Ce taux représente l'augmentation des charges annuelles de copropriété.")
            data["taux_croissance_charges_copro"], data["frequence_taux_croissance_charges_copro"] = input_with_frequency("Croissance des Charges de Copropriété (%)", "taux_croissance_charges_copro")

            # Croissance de la Taxe Foncière
            st.markdown("### Croissance de la Taxe Foncière (%)")
            st.markdown("Cette taxe locale peut augmenter au fil du temps.")
            data["taux_croissance_taxe_fonciere"], data["frequence_taux_croissance_taxe_fonciere"] = input_with_frequency("Croissance de la Taxe Foncière (%)", "taux_croissance_taxe_fonciere")

            # Croissance des Frais d'Entretien
            st.markdown("### Croissance des Frais d'Entretien (%)")
            st.markdown("Estime l'augmentation des coûts d'entretien de la propriété.")
            data["taux_croissance_entretien"], data["frequence_taux_croissance_entretien"] = input_with_frequency("Croissance des Frais d'Entretien (%)", "taux_croissance_entretien")

            # Croissance du Coût de l'Assurance PNO
            st.markdown("### Croissance du Coût de l'Assurance PNO (%)")
            st.markdown("Représente l'augmentation du coût de l'assurance propriétaire non occupant (PNO).")
            data["taux_croissance_assurance_pno"], data["frequence_taux_croissance_assurance_pno"] = input_with_frequency("Croissance du Coût de l'Assurance PNO (%)", "taux_croissance_assurance_pno")

            # Croissance du Coût de l'Assurance Emprunteur
            st.markdown("### Croissance du Coût de l'Assurance Emprunteur (%)")
            st.markdown("Ce taux indique l'augmentation attendue de cette assurance.")
            data["taux_croissance_assurance_emprunteur"], data["frequence_taux_croissance_assurance_emprunteur"] = input_with_frequency("Croissance du Coût de l'Assurance Emprunteur (%)", "taux_croissance_assurance_emprunteur")

            # Croissance des Travaux
            st.markdown("### Croissance des Coûts des Travaux (%)")
            st.markdown("L'inflation dans le secteur de la construction peut entraîner une hausse des coûts des travaux futurs.")
            data["taux_croissance_cout_travaux"], data["frequence_taux_croissance_cout_travaux"] = input_with_frequency("Croissance des Coûts des Travaux (%)", "taux_croissance_cout_travaux")

            # Taux d'Actualisation
            st.markdown("### Taux d'Actualisation (%)")
            st.markdown("Le taux d'actualisation est utilisé pour déterminer la valeur actuelle des flux futurs.")
            data["taux_actualisation"], data["frequence_taux_actualisation"] = input_with_frequency("Taux d'Actualisation (%)", "taux_actualisation")

            # Croissance des Revenus Personnels
            st.markdown("### Croissance des Revenus Personnels (%)")
            st.markdown("Estime l'évolution annuelle de tes revenus personnels.")
            data["taux_croissance_revenus"], data["frequence_taux_croissance_revenus"] = input_with_frequency("Croissance des Revenus Personnels (%)", "taux_croissance_revenus")

            DataStore.set("croissance", data)
