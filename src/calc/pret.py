import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Any, Optional

from src.calc.base_compute import BaseCompute

class PretCompute(BaseCompute):
    """
    Classe pour calculer les paiements de prêts basés sur différents contrats de financement.
    Permet de gérer plusieurs prêts, avec leurs dates de début et de fin, taux d'intérêt,
    périodicité, différé, remboursements anticipés et indexation.
    
    Cette classe génère un DataFrame quotidien des paiements de prêts et calcule
    diverses statistiques agrégées.
    """
    
    def __init__(self):
        """
        Initialise la classe avec les données de prêts depuis le DataStore.
        """
        super().__init__()
        
        # Récupérer les données depuis le DataStore
        self.prets = self.data.get("prets", [])
        self.croissance = self.data.get("croissance", {
            "taux_croissance_assurance_emprunteur": 2.5,
            "taux_inflation": 2.0
        })
        self.date_debut_simulation = self.data.get("date_debut_simulation", date.today())
        self.date_fin_simulation = self.data.get("date_fin_simulation", date.today() + relativedelta(years=10))
        
        # Initialiser les résultats
        self.results = {}
        self.df_prets = None
        
        # Créer le DataFrame de base avec toutes les dates
        self._creer_df_dates()
    
    def _creer_df_dates(self):
        """
        Crée le DataFrame de base avec toutes les dates de la simulation.
        """
        date_range = pd.date_range(
            start=self.date_debut_simulation, 
            end=self.date_fin_simulation, 
            freq='D'
        )
        
        self.df_dates = pd.DataFrame({
            'date': date_range,
            'paiement_total': 0.0,
            'principal_total': 0.0,
            'interets_total': 0.0,
            'frais_total': 0.0,
            'capital_restant_total': 0.0
        })
    
    def run(self):
        """
        Crée un DataFrame des paiements quotidiens pour tous les prêts.
        Execute tous les calculs et stocke les résultats dans le ResultStore.
        """
        if not self.prets:
            # Aucun prêt défini, créer un DataFrame vide
            self.df_prets = pd.DataFrame(columns=[
                'date', 'paiement_total', 'principal_total', 
                'interets_total', 'frais_total', 'capital_restant_total'
            ])
            self._stocker_resultats_vides()
            return
        
        # Copier le DataFrame de base
        self.df_prets = self.df_dates.copy()
        
        # Traiter chaque prêt
        for pret in self.prets:
            self._calculer_pret(pret)
        
        # Calculer les totaux
        self._calculer_totaux()
        
        # Calculer les statistiques
        self._calculer_statistiques_prets()
        self._stocker_resultats()
    
    def _calculer_pret(self, pret: Dict[str, Any]):
        """
        Calcule et ajoute les paiements d'un prêt au DataFrame.
        
        Args:
            pret (Dict): Informations sur le prêt
        """
        # Extraire les informations du prêt
        nom_pret = pret.get('label', pret.get('pret', f"Pret_{pret.get('id', '')}"))
        montant = pret.get('montant', 0)
        taux_interet = pret.get('taux_interet', 0) / 100
        duree_mois = pret.get('duree_mois', pret.get('duree_annees', 1) * 12)
        start_date = pd.to_datetime(pret.get('start_date'))
        
        # Paramètres avancés avec valeurs par défaut
        periodicite = pret.get('periodicite', 'Mensuelle')
        differe = pret.get('differe', {'active': False})
        remboursement_option = pret.get('remboursement_option', "À la date de début du prêt")
        remboursements_anticipes = pret.get('remboursements_anticipes', [])
        
        # Frais du prêt
        frais = {
            'frais_dossier': pret.get('frais_dossier', 0),
            'frais_courtage': pret.get('frais_courtage', 0),
            'frais_divers': pret.get('frais_divers', 0),
            'frais_caution': pret.get('frais_caution', 0),
            'frais_garantie_hypothecaire': pret.get('frais_garantie_hypothecaire', 0),
            'frais_assurance': pret.get('frais_assurance', 0)
        }
        
        # Calculer le tableau d'amortissement
        amortissement = self._calculer_amortissement_pret(
            montant, taux_interet, duree_mois, start_date,
            periodicite, differe, remboursement_option, remboursements_anticipes
        )
        
        # Ajouter au DataFrame principal
        self._ajouter_amortissement_au_df(amortissement, nom_pret, montant)
        
        # Ajouter les frais
        self._ajouter_frais_au_df(frais, start_date, nom_pret, montant)
        
        # Ajouter les calculs en valeur réelle
        self._ajouter_croissance_au_df(start_date, nom_pret)
    
    def _calculer_amortissement_pret(self, montant: float, taux_annuel: float, 
                                   duree_mois: int, start_date: pd.Timestamp,
                                   periodicite: str = 'Mensuelle',
                                   differe: Dict = None,
                                   remboursement_option: str = "À la date de début du prêt",
                                   remboursements_anticipes: List = None) -> pd.DataFrame:
        """
        Calcule le tableau d'amortissement pour un prêt.
        
        Returns:
            pd.DataFrame: Tableau d'amortissement avec colonnes [date_paiement, paiement, principal, interets, capital_restant]
        """
        # Mapping des périodicités
        periodicite_map = {
            'Mensuelle': {'periodes_par_an': 12, 'delta': relativedelta(months=1)},
            'Trimestrielle': {'periodes_par_an': 4, 'delta': relativedelta(months=3)},
            'Semestrielle': {'periodes_par_an': 2, 'delta': relativedelta(months=6)},
            'Annuelle': {'periodes_par_an': 1, 'delta': relativedelta(years=1)}
        }
        
        info_periodicite = periodicite_map.get(periodicite, periodicite_map['Mensuelle'])
        periodes_par_an = info_periodicite['periodes_par_an']
        delta_periode = info_periodicite['delta']
        
        # Calculer le taux par période
        taux_par_periode = taux_annuel / periodes_par_an
        nb_periodes = int(duree_mois / (12 / periodes_par_an))
        
        # Calculer la date du premier remboursement
        date_premier_paiement = self._calculer_date_premier_remboursement(
            start_date, periodicite, remboursement_option
        )
        
        # Générer les dates de paiement
        dates_paiement = []
        date_courante = date_premier_paiement
        for i in range(nb_periodes):
            dates_paiement.append(date_courante)
            date_courante = date_courante + delta_periode
        
        # Créer le DataFrame d'amortissement
        amortissement = pd.DataFrame({
            'date_paiement': dates_paiement,
            'paiement': 0.0,
            'principal': 0.0,
            'interets': 0.0,
            'capital_restant': montant
        })
        
        # Calculer la mensualité standard
        if taux_par_periode > 0:
            paiement_periodique = montant * (taux_par_periode * (1 + taux_par_periode) ** nb_periodes) / \
                                ((1 + taux_par_periode) ** nb_periodes - 1)
        else:
            paiement_periodique = montant / nb_periodes
        
        # Remplir le tableau d'amortissement
        capital_restant = montant
        
        for idx in range(len(amortissement)):
            interets = capital_restant * taux_par_periode
            principal = paiement_periodique - interets
            
            # S'assurer que le principal ne dépasse pas le capital restant
            if principal > capital_restant:
                principal = capital_restant
                paiement_periodique = principal + interets
            
            amortissement.loc[idx, 'interets'] = interets
            amortissement.loc[idx, 'principal'] = principal
            amortissement.loc[idx, 'paiement'] = paiement_periodique
            
            capital_restant -= principal
            amortissement.loc[idx, 'capital_restant'] = capital_restant
            
            if capital_restant <= 0:
                amortissement = amortissement[:idx+1].copy()
                break
        
        return amortissement
    
    def _calculer_date_premier_remboursement(self, start_date: pd.Timestamp, 
                                           periodicite: str, 
                                           option: str) -> pd.Timestamp:
        """
        Calcule la date du premier remboursement selon l'option choisie.
        """
        if option == "À la date de début du prêt":
            return start_date
            
        elif option == "Au début de la période suivante":
            if periodicite == 'Mensuelle':
                return start_date + relativedelta(day=1, months=1)
            elif periodicite == 'Trimestrielle':
                mois_actuel = start_date.month
                mois_prochain_trimestre = 3 * ((mois_actuel - 1) // 3 + 1) + 1
                if mois_prochain_trimestre > 12:
                    return pd.Timestamp(start_date.year + 1, mois_prochain_trimestre - 12, 1)
                else:
                    return pd.Timestamp(start_date.year, mois_prochain_trimestre, 1)
            # ... autres cas
            
        elif option == "À la fin de la première période":
            if periodicite == 'Mensuelle':
                return start_date + relativedelta(day=31, months=0)
            # ... autres cas
            
        return start_date
    
    def _ajouter_amortissement_au_df(self, amortissement: pd.DataFrame, 
                                   nom_pret: str, montant_initial: float):
        """
        Ajoute les données d'amortissement au DataFrame principal.
        """
        # Créer les colonnes pour ce prêt
        colonnes = [
            f'principal_{nom_pret}',
            f'interets_{nom_pret}', 
            f'paiement_{nom_pret}',
            f'capital_restant_{nom_pret}'
        ]
        
        for col in colonnes:
            self.df_prets[col] = 0.0
        
        # Fusionner les données d'amortissement
        for _, row in amortissement.iterrows():
            date_paiement = pd.to_datetime(row['date_paiement']).date()
            mask = self.df_prets['date'].dt.date == date_paiement
            
            if mask.any():
                self.df_prets.loc[mask, f'principal_{nom_pret}'] = row['principal']
                self.df_prets.loc[mask, f'interets_{nom_pret}'] = row['interets']
                self.df_prets.loc[mask, f'paiement_{nom_pret}'] = row['paiement']
                self.df_prets.loc[mask, f'capital_restant_{nom_pret}'] = row['capital_restant']
        
        # Remplir le capital restant avec forward fill
        col_capital = f'capital_restant_{nom_pret}'
        # Initialiser avec le montant initial avant la première date
        premiere_date_paiement = amortissement['date_paiement'].min()
        mask_avant = self.df_prets['date'] < premiere_date_paiement
        self.df_prets.loc[mask_avant, col_capital] = montant_initial
        
        # Forward fill pour les dates suivantes
        self.df_prets[col_capital] = self.df_prets[col_capital].fillna(method='ffill')
        self.df_prets[col_capital] = self.df_prets[col_capital].fillna(0)
    
    def _ajouter_frais_au_df(self, frais: Dict[str, float], start_date: pd.Timestamp, 
                           nom_pret: str, montant_pret: float):
        """
        Ajoute les frais du prêt au DataFrame.
        """
        # Frais ponctuels à la date de début
        frais_ponctuels = {
            f'frais_dossier_{nom_pret}': frais['frais_dossier'],
            f'frais_courtage_{nom_pret}': frais['frais_courtage'],
            f'frais_divers_{nom_pret}': frais['frais_divers'],
        }
        
        # Frais proportionnels au montant
        frais_proportionnels = {
            f'frais_caution_{nom_pret}': montant_pret * frais['frais_caution'] / 100,
            f'frais_garantie_hypothecaire_{nom_pret}': montant_pret * frais['frais_garantie_hypothecaire'] / 100,
        }
        
        # Initialiser toutes les colonnes de frais
        tous_frais = {**frais_ponctuels, **frais_proportionnels}
        for col in tous_frais:
            self.df_prets[col] = 0.0
        
        # Ajouter les frais à la date de début
        date_debut = pd.to_datetime(start_date).date()
        mask_debut = self.df_prets['date'].dt.date == date_debut
        
        for col, montant in tous_frais.items():
            if montant > 0:
                self.df_prets.loc[mask_debut, col] = montant
        
        # Frais d'assurance annuels (31 décembre de chaque année)
        col_assurance = f'frais_assurance_{nom_pret}'
        self.df_prets[col_assurance] = 0.0
        
        if frais['frais_assurance'] > 0:
            mask_assurance = (self.df_prets['date'].dt.month == 12) & \
                           (self.df_prets['date'].dt.day == 31)
            self.df_prets.loc[mask_assurance, col_assurance] = frais['frais_assurance']
        
        # Calculer le total des frais pour ce prêt
        colonnes_frais = list(tous_frais.keys()) + [col_assurance]
        self.df_prets[f'frais_{nom_pret}'] = self.df_prets[colonnes_frais].sum(axis=1)
    
    def _ajouter_croissance_au_df(self, start_date: pd.Timestamp, nom_pret: str):
        """
        Ajoute les colonnes en valeur réelle (ajustées de l'inflation).
        """
        taux_inflation = self.croissance.get("taux_inflation", 2.0) / 100
        taux_croissance_assurance = self.croissance.get("taux_croissance_assurance_emprunteur", 2.5) / 100
        
        # Taux journaliers
        taux_inflation_journalier = (1 + taux_inflation) ** (1/365.25) - 1
        taux_croissance_assurance_journalier = (1 + taux_croissance_assurance) ** (1/365.25) - 1
        
        # Calculer les jours depuis le début
        jours_depuis_debut = (self.df_prets['date'] - pd.to_datetime(start_date)).dt.days
        
        # Facteur d'actualisation
        facteur_inflation = (1 + taux_inflation_journalier) ** jours_depuis_debut
        facteur_croissance_assurance = (1 + taux_croissance_assurance_journalier) ** jours_depuis_debut
        
        # Colonnes à ajuster pour l'inflation
        colonnes_a_ajuster = ['principal', 'interets', 'paiement', 'capital_restant', 'frais']
        
        for col in colonnes_a_ajuster:
            col_nominale = f'{col}_{nom_pret}'
            col_reelle = f'{col}_reel_{nom_pret}'
            
            if col_nominale in self.df_prets.columns:
                if col == 'frais':
                    # Les frais d'assurance croissent, les autres frais restent constants
                    col_assurance = f'frais_assurance_{nom_pret}'
                    if col_assurance in self.df_prets.columns:
                        frais_assurance_ajustes = self.df_prets[col_assurance] * facteur_croissance_assurance / facteur_inflation
                        autres_frais = self.df_prets[col_nominale] - self.df_prets[col_assurance]
                        autres_frais_ajustes = autres_frais / facteur_inflation
                        self.df_prets[col_reelle] = frais_assurance_ajustes + autres_frais_ajustes
                    else:
                        self.df_prets[col_reelle] = self.df_prets[col_nominale] / facteur_inflation
                else:
                    self.df_prets[col_reelle] = self.df_prets[col_nominale] / facteur_inflation
    
    def _calculer_totaux(self):
        """
        Calcule les colonnes de totaux pour tous les prêts.
        """
        # Préfixes des colonnes à totaliser
        prefixes = [
            'principal_', 'interets_', 'paiement_', 'frais_', 'capital_restant_',
            'principal_reel_', 'interets_reel_', 'paiement_reel_', 'frais_reel_', 'capital_restant_reel_'
        ]
        
        for prefix in prefixes:
            colonnes = [col for col in self.df_prets.columns if col.startswith(prefix) and not col.endswith('_total')]
            if colonnes:
                col_total = f'{prefix}total'
                self.df_prets[col_total] = self.df_prets[colonnes].sum(axis=1)
    
    def _calculer_statistiques_prets(self):
        """
        Calcule les statistiques détaillées sur les prêts.
        """
        if self.df_prets is None or self.df_prets.empty:
            return
        
        # Statistiques globales
        total_paiements = self.df_prets['paiement_total'].sum()
        total_principal = self.df_prets['principal_total'].sum()
        total_interets = self.df_prets['interets_total'].sum()
        total_frais = self.df_prets['frais_total'].sum()
        
        # Statistiques par prêt
        stats_par_pret = []
        
        for pret in self.prets:
            nom_pret = pret.get('label', pret.get('pret', f"Pret_{pret.get('id', '')}"))
            
            col_paiement = f'paiement_{nom_pret}'
            col_principal = f'principal_{nom_pret}'
            col_interets = f'interets_{nom_pret}'
            col_frais = f'frais_{nom_pret}'
            
            if col_paiement in self.df_prets.columns:
                stats_pret = {
                    'label': nom_pret,
                    'montant_initial': pret.get('montant', 0),
                    'total_paiements': float(self.df_prets[col_paiement].sum()),
                    'total_principal': float(self.df_prets[col_principal].sum()),
                    'total_interets': float(self.df_prets[col_interets].sum()),
                    'total_frais': float(self.df_prets[col_frais].sum()),
                    'taux_interet': pret.get('taux_interet', 0),
                    'duree_mois': pret.get('duree_mois', 0),
                    'start_date': pret.get('start_date'),
                    'periodicite': pret.get('periodicite', 'Mensuelle')
                }
                stats_par_pret.append(stats_pret)
        
        # Statistiques temporelles
        df_mensuel = self.df_prets.copy()
        df_mensuel['year_month'] = df_mensuel['date'].dt.strftime('%Y-%m')
        stats_mensuelles = df_mensuel.groupby('year_month').agg({
            'paiement_total': 'sum',
            'principal_total': 'sum', 
            'interets_total': 'sum',
            'frais_total': 'sum'
        }).reset_index()
        
        df_annuel = self.df_prets.copy()
        df_annuel['year'] = df_annuel['date'].dt.year
        stats_annuelles = df_annuel.groupby('year').agg({
            'paiement_total': 'sum',
            'principal_total': 'sum',
            'interets_total': 'sum', 
            'frais_total': 'sum'
        }).reset_index()
        
        # Stocker les résultats
        self.results = {
            'total_paiements': total_paiements,
            'total_principal': total_principal,
            'total_interets': total_interets,
            'total_frais': total_frais,
            'cout_total_credit': total_paiements + total_frais,
            'nb_prets': len(self.prets),
            'paiement_mensuel_moyen': float(stats_mensuelles['paiement_total'].mean()) if len(stats_mensuelles) > 0 else 0,
            'stats_par_pret': stats_par_pret,
            'stats_mensuelles': stats_mensuelles,
            'stats_annuelles': stats_annuelles,
            'df_prets_quotidiens': self.df_prets
        }
    
    def _stocker_resultats_vides(self):
        """
        Stocke des résultats vides quand aucun prêt n'est défini.
        """
        resultats_vides = {
            'total_paiements': 0,
            'total_principal': 0,
            'total_interets': 0,
            'total_frais': 0,
            'cout_total_credit': 0,
            'nb_prets': 0,
            'paiement_mensuel_moyen': 0,
            'stats_par_pret': [],
            'stats_mensuelles': pd.DataFrame(),
            'stats_annuelles': pd.DataFrame()
        }
        
        for key, value in resultats_vides.items():
            self.store_result(f"prets_{key}", value)
    
    def _stocker_resultats(self):
        """
        Stocke tous les résultats dans le ResultStore.
        """
        for key, value in self.results.items():
            if key != 'df_prets_quotidiens':  # DataFrame trop volumineux
                self.store_result(f"prets_{key}", value)
        
        # Stocker quelques métriques clés pour compatibilité
        self.store_result("cout_total_credit", self.results['cout_total_credit'])
        self.store_result("paiement_mensuel_moyen", self.results['paiement_mensuel_moyen'])
        self.store_result("nombre_prets", self.results['nb_prets'])
        self.store_result("prets_df_quotidien", self.results['df_prets_quotidiens'])
    
    def get_dataframe(self) -> pd.DataFrame:
        """
        Retourne le DataFrame des paiements quotidiens.
        
        Returns:
            pd.DataFrame: DataFrame des paiements quotidiens
        """
        return self.df_prets if self.df_prets is not None else pd.DataFrame()
    
    def get_results(self) -> Dict[str, Any]:
        """
        Retourne tous les résultats des calculs.
        
        Returns:
            dict: Résultats complets des calculs
        """
        return self.results

    def verifier_coherence(self) -> Dict[str, Any]:
        """
        Méthode pour vérifier la cohérence des calculs de prêts.
        
        Returns:
            dict: Rapport de vérification
        """
        if self.df_prets is None or self.df_prets.empty:
            return {"status": "error", "message": "Aucune donnée calculée"}
        
        # Analyser les variations mensuelles
        df_mensuel = self.df_prets.copy()
        df_mensuel['year_month'] = df_mensuel['date'].dt.strftime('%Y-%m')
        paiements_mensuels = df_mensuel.groupby('year_month')['paiement_total'].sum()
        
        rapport = {
            "total_mois": len(paiements_mensuels),
            "mois_zero": len(paiements_mensuels[paiements_mensuels == 0]),
            "montant_min": float(paiements_mensuels.min()),
            "montant_max": float(paiements_mensuels.max()),
            "montant_moyen": float(paiements_mensuels.mean()),
            "variation_pct": float((paiements_mensuels.std() / paiements_mensuels.mean()) * 100) if paiements_mensuels.mean() > 0 else 0
        }
        
        # Diagnostics
        if rapport["mois_zero"] > 0:
            rapport["alerte_mois_zero"] = f"{rapport['mois_zero']} mois ont un paiement de 0€"
        
        if rapport["variation_pct"] > 10:
            rapport["alerte_variation"] = f"Forte variation détectée: {rapport['variation_pct']:.1f}%"
        
        return rapport
