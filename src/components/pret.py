import streamlit as st
from dateutil.relativedelta import relativedelta

from src.utils.data_store import DataStore 

class Pret:
    
    @staticmethod
    def render():
        with st.expander("2️⃣ Paramètres de Prêt – *Cliquez pour ouvrir*", expanded=False):
            
            label_pret = [f"Prêt {i+1}" for i in range(5)]
            onglets = st.tabs(label_pret)
            prets = []

            for i, onglet in enumerate(onglets):
                with onglet:
                    st.subheader(f"Paramètres pour {label_pret[i]}")
                    st.divider()
                    active = st.checkbox("Activer / Désactiver", key=f"activer_{i}")

                    if active:
                        st.success(f"{label_pret[i]} est **activé**.")
                    else:
                        st.warning(f"{label_pret[i]} est **désactivé**.")

                    
                    # Durée
                    utiliser_mois = st.checkbox("Exprimer la Durée en Mois", key=f"utiliser_mois_{i}")
                    if utiliser_mois:
                        duree_mois = st.number_input("Durée du Prêt (Mois)", min_value=1, max_value=600, step=1, value=240, key=f"duree_mois_{i}")
                        duree_annees = duree_mois / 12
                    else:
                        duree_annees = st.number_input("Durée du Prêt (Années)", min_value=1, max_value=50, step=1, value=20, key=f"duree_annees_{i}")
                        duree_mois = duree_annees * 12
                    
                    # Date 
                    start_date = st.date_input("Date de Début", key=f"start_date_pret_{i}")
                    end_date = start_date + relativedelta(months=duree_mois)
                    
                    # Selectbox pour le démarrage du remboursement
                    remboursement_option = st.selectbox(
                        "Début du remboursement",
                        options=[
                            "À la date de début du prêt",
                            "Au début de la période suivante",
                            "À la fin de la première période"
                        ],
                        index=0,
                        key=f"remboursement_option_{i}"
                    )
                    
                    cash_apport = st.number_input("Apport Cash (€)", min_value=0, max_value=10_000_000, value=0, step=1, key=f"apport_{i}")
                    montant_pret = st.number_input("Montant du Prêt (€)", min_value=1000, max_value=10_000_000, value=100_000, step=1, key=f"montant_{i}")
                    taux_interet = st.number_input("Taux d'Intérêt Annuel (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1, key=f"taux_{i}")

                    # Type de taux
                    type_taux = st.selectbox(
                        "Type de Taux", 
                        options=["Fixe", "Variable", "Capé", "Taux Mixte"],
                        index=0,
                        key=f"type_taux_{i}"
                    )

                    # Périodicité des remboursements
                    periodicite = st.selectbox(
                        "Périodicité des Remboursements", 
                        options=["Mensuelle", "Trimestrielle", "Semestrielle", "Annuelle"],
                        index=0,
                        key=f"periodicite_{i}"
                    )

                    # Type de remboursement
                    type_remboursement = st.selectbox(
                        "Type de Remboursement", 
                        options=["Amortissable", "Intérêts Seulement", "In Fine"],
                        index=0,
                        key=f"type_remboursement_{i}"
                    )



                    

                    st.markdown("### Frais Relatifs au Prêt")
                    frais_dossier = st.number_input("Frais de Dossier (en €)", min_value=0.0, value=500.0, step=50.0, key=f"frais_dossier_{i}")
                    frais_assurance = st.number_input("Frais d'Assurance (en €)", min_value=0.0, value=300.0, step=50.0, key=f"frais_assurance_{i}")
                    frais_caution = st.number_input("Frais de Caution / Garantie (%)", min_value=0.0, max_value=5.0, value=1.0, step=0.1, key=f"frais_caution_{i}")

                    st.markdown("### Frais de Garanties et Autres Frais")
                    frais_garantie_hypothecaire = st.number_input("Frais de Garantie Hypothécaire (%)", min_value=0.0, max_value=5.0, value=1.5, step=0.1, key=f"frais_garantie_hypothecaire_{i}")
                    frais_courtage = st.number_input("Frais de Courtage (en €)", min_value=0.0, value=500.0, step=100.0, key=f"frais_courtage_{i}")

                    st.markdown("### Frais Annexes (Autres frais spécifiques)")
                    frais_divers = st.number_input("Frais Divers (en €)", min_value=0.0, value=0.0, step=50.0, key=f"frais_divers_{i}")
                    
                    # Différé
                    st.markdown("### Différé")

                    activer_differe = st.checkbox("Activer un différé de remboursement ?", key=f"activer_differe_{i}")

                    if activer_differe:
                        duree_differe = st.number_input(
                            "Durée du Différé (en mois)",
                            min_value=1, max_value=60, value=12, step=1,
                            key=f"differe_duree_{i}"
                        )

                        type_differe = st.selectbox(
                            "Type de Différé",
                            options=["Partiel (Intérêts)", "Total (Pas de paiement)"],
                            key=f"type_differe_{i}"
                        )

                        personnaliser_taux_differe = st.checkbox("Personnaliser le taux d'intérêt pendant le différé ?", key=f"perso_taux_differe_{i}")
                        
                        if personnaliser_taux_differe:
                            taux_dans_differe = st.number_input(
                                "Taux d'intérêt pendant le différé (%)",
                                min_value=0.0, max_value=100.0,
                                value=taux_interet, step=0.1,
                                key=f"taux_differe_{i}"
                            )
                        else:
                            taux_dans_differe = taux_interet
                    else:
                        duree_differe = 0
                        type_differe = "Aucun"
                        taux_dans_differe = taux_interet

                    # Remboursements anticipés
                    st.markdown("### Remboursements Anticipés")

                    nb_anticipes = st.number_input(
                        "Nombre de remboursements anticipés",
                        min_value=0, max_value=10, step=1, value=0, key=f"nb_anticipes_{i}"
                    )

                    remboursements_anticipes = []

                    if nb_anticipes > 0:
                        st.markdown("""<style>.stDataFrame tbody tr th { display: none; }</style>""", unsafe_allow_html=True)
                        st.markdown("#### Paramètres des remboursements anticipés")

                        for j in range(nb_anticipes):
                            with st.container():
                                cols = st.columns([2, 2, 2, 2])
                                with cols[0]:
                                    montant = st.number_input(
                                        f"Montant (€) {j+1}", min_value=0, value=0, step=100,
                                        key=f"montant_anticipe_{i}_{j}"
                                    )
                                with cols[1]:
                                    date = st.date_input(f"Date {j+1}", key=f"date_anticipe_{i}_{j}")
                                with cols[2]:
                                    penalite = st.number_input(
                                        f"Pénalité (%) {j+1}", min_value=0.0, max_value=100.0, step=0.1, value=3.0,
                                        key=f"penalite_{i}_{j}"
                                    )
                                with cols[3]:
                                    type_anticipe = st.selectbox(
                                        f"Type {j+1}", options=["Partiel", "Total"],
                                        key=f"type_anticipe_{i}_{j}"
                                    )

                                remboursements_anticipes.append({
                                    "montant": montant,
                                    "date": date,
                                    "penalite": penalite,
                                    "type": type_anticipe
                                })

                    # Création de l'objet du prêt à enregistrer dans DataStore
                    if active:
                        prets.append(
                            {
                                "pret": f"pret_{i+1}",
                                "cash_apport":cash_apport,
                                "montant": montant_pret,
                                "taux_interet": taux_interet,
                                "type_taux": type_taux,
                                "frais_dossier": frais_dossier,
                                "frais_assurance": frais_assurance,
                                "frais_caution": frais_caution,
                                "frais_garantie_hypothecaire": frais_garantie_hypothecaire,
                                "frais_courtage": frais_courtage,
                                "frais_divers": frais_divers,
                                "type_remboursement": type_remboursement,
                                "duree_mois": duree_mois,
                                "start_date": start_date,
                                "end_date": end_date,
                                "remboursement_option": remboursement_option,
                                "periodicite": periodicite,
                                "differe": {
                                    "active": activer_differe,
                                    "duree": duree_differe if activer_differe else 0,
                                    "type": type_differe if activer_differe else "Aucun",
                                    "taux": taux_dans_differe  # Ce taux a déjà été ajusté selon la checkbox plus haut
                                },
                                "remboursements_anticipes": remboursements_anticipes
                            }
                        )

            # Enregistrement des données dans DataStore
            DataStore.set("prets", prets)