from datetime import timedelta
import streamlit as st
from dateutil.relativedelta import relativedelta

from src.utils.data_store import DataStore 

class Loyer:
    
    @staticmethod
    def render():
        with st.expander("3️⃣ Paramètres de Loyer – *Cliquez pour ouvrir*", expanded=False):
    
            label_loyer = [f"Loyer {i+1}" for i in range(5)]
            onglets = st.tabs(label_loyer)
            loyers = []

            # Chaque onglet de loyer
            for i, onglet in enumerate(onglets):
                with onglet:
                    st.subheader(f"Paramètres pour {label_loyer[i]}")
                    st.divider()
                    
                    active = st.checkbox("Activer / Désactiver", key=f"loyer_activer_{i}")

                    if active:
                        st.success(f"{label_loyer[i]} est **activé**.")
                    else:
                        st.warning(f"{label_loyer[i]} est **désactivé**.")

                    # Entrées de loyer mensuel
                    loyer_mensuel = st.number_input("Montant du Loyer Mensuel (€)", min_value=0, value=1400, step=10, key=f"loyer_mensuel_{i}")
                    charges_mensuelles = st.number_input("Charges Mensuelles (optionnel) (€)", min_value=0, value=20, step=5, key=f"charges_mensuelles_{i}")
                    
                    # Jour de paiement
                    dernier_jour = st.checkbox("Paiement le dernier jour du mois ?", key=f"dernier_jour_{i}")

                    if not dernier_jour:
                        jour_paiement = st.number_input(
                            "Jour du Paiement (1 à 28 recommandé pour éviter les problèmes de mois court)",
                            min_value=1, max_value=28, step=1, value=1, key=f"jour_paiement_{i}"
                        )
                    else:
                        jour_paiement = "last"

                    
                    # Basculement d'entrée de durée
                    utiliser_mois = st.checkbox("Exprimer la Durée en Mois", key=f"utiliser_mois_loyer_{i}")

                    if utiliser_mois:
                        duree_contrat_mois = st.number_input("Durée du Contrat (Mois)", min_value=1, max_value=600, step=1, value=36, key=f"contrat_mois_{i}")
                        duree_contrat_annees = duree_contrat_mois / 12
                    else:
                        duree_contrat_annees = st.number_input("Durée du Contrat (Années)", min_value=1, max_value=50, step=1, value=25, key=f"contrat_annees_{i}")
                        duree_contrat_mois = duree_contrat_annees * 12

                    # Date de début
                    start_date = st.date_input("Date de Début", key=f"start_date_loyer_{i}")
                    end_date = start_date + relativedelta(months=duree_contrat_mois)

                    # Frais
                    st.markdown("#### Frais")
                    tx_gli = st.number_input("GLI - Assurance Garantie des Loyers (%)", min_value=0.0, max_value=20.0, step=0.01, value=3.0, key=f"gli_{i}")
                    
                    # Indexation
                    st.markdown("#### Indexation")
                    
                    # Indexation personnalisée
                    freq_idx = st.number_input("Indexation Frequency (Années)", min_value=0, max_value=50, step=1, value=5, key=f"index_frequency_{i}")
                    tx_idx = st.number_input("Indexation Taux (%)", min_value=0.0, max_value=20.0, step=0.01, value=1.0, key=f"index_taux_{i}")
                    
                    # Date de réindexation pour tx_idx
                    mode_idx = st.radio(
                        "Quand appliquer l'indexation personnalisée ?",
                        options=["1er janvier", "Anniversaire du contrat"],
                        key=f"mode_idx_{i}"
                    )
                    
                    if mode_idx == "1er janvier":
                        date_idx_mode = "january"
                        date_idx = None
                    else:
                        date_idx_mode = "anniversary"
                        date_idx = start_date  # On stocke la date de début pour référence

                    # IRL
                    tx_irl = st.number_input("IRL - Indice de Référence des Loyers (%)", min_value=0.0, max_value=20.0, step=0.01, value=1.0, key=f"irl_{i}")
                    
                    # Date de réindexation pour tx_irl
                    mode_irl = st.radio(
                        "Quand appliquer l'IRL ?",
                        options=["1er janvier", "Anniversaire du contrat"],
                        key=f"mode_irl_{i}"
                    )
                    
                    if mode_irl == "1er janvier":
                        date_irl_mode = "january"
                        date_irl = None
                    else:
                        date_irl_mode = "anniversary"
                        date_irl = start_date  # On stocke la date de début pour référence

                    # Taux d'occupation
                    st.markdown("#### Taux d'Occupation")
                    mode_occupation = st.radio(
                        "Choisissez comment exprimer l'occupation:",
                        options=["En %", "En mois", "En jours"],
                        horizontal=True,
                        key=f"mode_occupation_{i}"
                    )

                    if mode_occupation == "En %":
                        taux_occupation = st.number_input(
                            "Taux d'Occupation (%)", min_value=0.0, max_value=100.0, value=90.0, step=1.0, key=f"taux_occupation_{i}"
                        )
                        mois_occupes = round(taux_occupation / 100 * 12, 1)
                        jours_occupes = round(taux_occupation / 100 * 365, 1)
                        st.info(f"≈ {mois_occupes} mois ou {jours_occupes} jours occupés par an.")

                    elif mode_occupation == "En mois":
                        mois_occupes = st.number_input(
                            "Nombre de Mois Occupés par An", min_value=0.0, max_value=12.0, value=12.0, step=0.1, key=f"mois_occupes_{i}"
                        )
                        taux_occupation = round(mois_occupes / 12 * 100, 1)
                        jours_occupes = round(mois_occupes * 30.4, 1)
                        st.info(f"≈ {taux_occupation}% ou {jours_occupes} jours occupés par an.")

                    elif mode_occupation == "En jours":
                        jours_occupes = st.number_input(
                            "Nombre de Jours Occupés par An", min_value=0.0, max_value=365.0, value=365.0, step=1.0, key=f"jours_occupes_{i}"
                        )
                        taux_occupation = round(jours_occupes / 365 * 100, 1)
                        mois_occupes = round(jours_occupes / 30.4, 1)
                        st.info(f"≈ {taux_occupation}% ou {mois_occupes} mois occupés par an.")
                        
                    if active:
                        loyers.append(
                            {
                                "label": label_loyer[i],
                                "loyer_mensuel": loyer_mensuel,
                                "jour_paiement": jour_paiement,
                                "charges_mensuelles": charges_mensuelles,
                                "duree_contrat_mois": duree_contrat_mois,
                                "duree_contrat_annees": duree_contrat_annees,
                                "start_date": start_date,
                                "end_date": end_date,
                                "tx_gli": tx_gli,
                                "freq_idx": freq_idx,
                                "tx_idx": tx_idx,
                                "date_idx_mode": date_idx_mode,
                                "date_idx": date_idx,
                                "tx_irl": tx_irl,
                                "date_irl_mode": date_irl_mode,
                                "date_irl": date_irl,
                                "taux_occupation": taux_occupation,
                                "mois_occupes": mois_occupes
                            }
                        )

            # Enregistrement des données dans DataStore
            DataStore.set("loyers", loyers)