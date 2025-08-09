import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Any, Optional
import calendar

from src.utils.result_store import ResultStore
from src.calc.base_compute import BaseCompute

class LoyerCompute(BaseCompute):
    """
    Classe optimisée pour calculer les revenus locatifs basés sur différents contrats de location.
    Permet de gérer plusieurs baux, avec leurs dates de début et de fin, taux d'occupation,
    indexation personnalisée, IRL et GLI.
    
    Cette classe génère un DataFrame quotidien des revenus locatifs et calcule
    diverses statistiques agrégées de manière optimisée.
    """
    
    def __init__(self):
        """
        Initialise la classe avec les données de loyers depuis le DataStore.
        Les dates de simulation sont automatiquement calculées basées sur les contrats.
        """
        super().__init__()
        
        self.loyers = self.data.get("loyers", [])
        
        self.results = {}
        self.results_par_loyer = {}  # Nouveau dictionnaire pour stocker les résultats individuels
        self.result_store = ResultStore()
        
        self._get_simulation_dates()
        self._init_df()
        
        self.df_mensuelles_consolidé = pd.DataFrame()
        self.df_mensuelles_détaillés = pd.DataFrame()
    
    def _get_simulation_dates(self):
        start_dates = []
        end_dates = []
        
        for loyer in self.loyers:
            start_date = loyer.get('start_date')
            end_date = loyer.get('end_date')
            start_dates.append(start_date)
            end_dates.append(end_date)
        
        self.start_date = min(start_dates)
        self.end_date = max(end_dates)

    def _init_df(self):
        date_range = pd.date_range(start=self.start_date,end=self.end_date,freq='D')
        
        self.df_dates = pd.DataFrame({
            'date': date_range,
            'loyer': 0.0,
            'charges': 0.0,
            'total': 0.0,
            'loyer_irl': 0.0,
            'loyer_idx': 0.0,
            'frais_gli': 0.0
        })
        
        self.df_dates['year'] = self.df_dates['date'].dt.year
        self.df_dates['month'] = self.df_dates['date'].dt.month
        self.df_dates['year_month'] = self.df_dates['date'].dt.strftime('%Y-%m')
        self.df_loyers = self.df_dates.copy()
    
    def run(self):
        """
        Execute tous les calculs en mode optimisé ou standard selon la durée.
        """
        for loyer in self.loyers:
            self._calculer_mensualite(loyer)
            
        self._calculer_statistiques_base()
        
        self._stocker_resultats()
    
    def _calculer_mensualite(self, loyer: Dict[str, Any]) -> None:
        
        label = loyer.get('label', 'Loyer sans nom')
        start_date = pd.to_datetime(loyer.get('start_date')).date()
        end_date = pd.to_datetime(loyer.get('end_date')).date()

        loyer_mensuel_base = loyer.get('loyer_mensuel', 0)
        charges_mensuelles_base = loyer.get('charges_mensuelles', 0)
        taux_occupation = loyer.get('taux_occupation', 100) / 100
        tx_gli = loyer.get('tx_gli', 0.0) / 100

        mensualites_data = []

        current_date = start_date.replace(day=1)
        end_date_month = end_date.replace(day=1)

        while current_date <= end_date_month:
            
            year = current_date.year
            month = current_date.month
            year_month = current_date.strftime('%Y-%m')

            facteur_indexation = self._calc_facteur_index(loyer, year, month)
            facteur_irl = self._calc_facteur_irl(loyer, year, month)

            # Calculer les montants mensuels - CORRECTION ICI
            loyer_mensuel = loyer_mensuel_base * taux_occupation  # Sans indexation
            loyer_mensuel_idx = loyer_mensuel_base * facteur_indexation * taux_occupation  # Avec indexation personnalisée
            loyer_mensuel_irl = loyer_mensuel_base * facteur_irl * taux_occupation  # Avec IRL
            charges_mensuelles = charges_mensuelles_base * taux_occupation
            total_mensuel = loyer_mensuel_idx + charges_mensuelles  # Le total utilise le loyer indexé
            frais_gli_mensuel = total_mensuel * tx_gli
            net_total_mensuel = total_mensuel - frais_gli_mensuel

            # Ajouter la mensualité à la liste - CORRECTION ICI
            mensualite_data = {
                'year_month': year_month,
                'year': year,
                'month': month,
                
                'loyer': float(loyer_mensuel),  # Loyer de base sans indexation
                'loyer_idx': float(loyer_mensuel_idx),  # Loyer avec indexation personnalisée
                'loyer_irl': float(loyer_mensuel_irl),  # Loyer avec IRL
                'charges': float(charges_mensuelles),
                'total': float(total_mensuel),  # Total = loyer_idx + charges
                'net_total': float(net_total_mensuel),  # Net = total - GLI
                'frais_gli': float(frais_gli_mensuel),
                
                'taux_occupation': float(taux_occupation * 100),
                'facteur_indexation': float(facteur_indexation),
                'facteur_irl': float(facteur_irl),
            }

            mensualites_data.append(mensualite_data)

            # Passer au mois suivant
            current_date += relativedelta(months=1)

            if current_date > end_date_month:
                break

        # Convertir en DataFrame pour ce loyer
        df_loyer = pd.DataFrame(mensualites_data)
        
        # ===== NOUVEAU : Calculer les statistiques pour ce loyer individuel =====
        total_loyers_base_loyer = float(df_loyer['loyer'].sum())  # Total des loyers de base
        total_loyers_idx_loyer = float(df_loyer['loyer_idx'].sum())  # Total des loyers indexés
        total_loyers_irl_loyer = float(df_loyer['loyer_irl'].sum())  # Total des loyers IRL
        total_charges_loyer = float(df_loyer['charges'].sum())
        total_brut_loyer = float(df_loyer['total'].sum())  # Total brut (loyer_idx + charges)
        total_net_loyer = float(df_loyer['net_total'].sum())  # Total net (après GLI)
        total_frais_gli_loyer = float(df_loyer['frais_gli'].sum())
        
        # Calculer les stats annuelles pour ce loyer
        stats_annuelles_loyer = df_loyer.groupby('year').agg({
            'loyer': 'sum',
            'loyer_idx': 'sum',
            'loyer_irl': 'sum',
            'charges': 'sum',
            'total': 'sum',
            'net_total': 'sum',
            'frais_gli': 'sum'
        }).reset_index()
        
        # Stocker les résultats pour ce loyer spécifique
        self.results_par_loyer[label] = {
            'label': label,
            'start_date': start_date,
            'end_date': end_date,
            'loyer_mensuel_base': loyer_mensuel_base,
            'charges_mensuelles_base': charges_mensuelles_base,
            'taux_occupation': taux_occupation * 100,
            'tx_gli': tx_gli * 100,
            
            # Totaux différenciés
            'total_loyers_base': total_loyers_base_loyer,  # Sans indexation
            'total_loyers_idx': total_loyers_idx_loyer,    # Avec indexation personnalisée
            'total_loyers_irl': total_loyers_irl_loyer,    # Avec IRL
            'total_charges': total_charges_loyer,
            'total_brut': total_brut_loyer,               # Loyer indexé + charges
            'total_net': total_net_loyer,                 # Après déduction GLI
            'total_frais_gli': total_frais_gli_loyer,
            
            'nb_mois': len(df_loyer),
            'df_mensuel': df_loyer,
            'df_annuel': stats_annuelles_loyer,
            
            # Moyennes mensuelles différenciées
            'loyer_base_mensuel_moyen': total_loyers_base_loyer / max(len(df_loyer), 1),
            'loyer_idx_mensuel_moyen': total_loyers_idx_loyer / max(len(df_loyer), 1),
            'loyer_irl_mensuel_moyen': total_loyers_irl_loyer / max(len(df_loyer), 1),
            'charges_mensuelles_moyennes': total_charges_loyer / max(len(df_loyer), 1),
        }
        
        # Stocker dans df_mensuelles_détaillés (une colonne par loyer)
        if self.df_mensuelles_détaillés.empty:
            self.df_mensuelles_détaillés = df_loyer[['year_month', 'year', 'month']].copy()
        
        self.df_mensuelles_détaillés[f'{label}_loyer_base'] = df_loyer['loyer']
        self.df_mensuelles_détaillés[f'{label}_loyer_idx'] = df_loyer['loyer_idx']
        self.df_mensuelles_détaillés[f'{label}_loyer_irl'] = df_loyer['loyer_irl']
        self.df_mensuelles_détaillés[f'{label}_charges'] = df_loyer['charges']
        self.df_mensuelles_détaillés[f'{label}_total_brut'] = df_loyer['total']
        self.df_mensuelles_détaillés[f'{label}_total_net'] = df_loyer['net_total']
        self.df_mensuelles_détaillés[f'{label}_frais_gli'] = df_loyer['frais_gli']
        
        # Stocker dans df_mensuelles_consolidé (somme de tous les loyers)
        if self.df_mensuelles_consolidé.empty:
            self.df_mensuelles_consolidé = df_loyer[['year_month', 'year', 'month']].copy()
            self.df_mensuelles_consolidé['loyer_base_total'] = df_loyer['loyer']
            self.df_mensuelles_consolidé['loyer_idx_total'] = df_loyer['loyer_idx']
            self.df_mensuelles_consolidé['loyer_irl_total'] = df_loyer['loyer_irl']
            self.df_mensuelles_consolidé['charges_total'] = df_loyer['charges']
            self.df_mensuelles_consolidé['total_brut'] = df_loyer['total']
            self.df_mensuelles_consolidé['total_net'] = df_loyer['net_total']
            self.df_mensuelles_consolidé['frais_gli_total'] = df_loyer['frais_gli']
            
        else:
            # Merger et sommer les valeurs
            temp_df = df_loyer[['year_month', 'loyer', 'loyer_idx', 'loyer_irl', 'charges', 'total', 'net_total', 'frais_gli']].copy()
            temp_df.columns = ['year_month', 'loyer_base_total', 'loyer_idx_total', 'loyer_irl_total', 'charges_total', 'total_brut', 'total_net', 'frais_gli_total']
            
            self.df_mensuelles_consolidé = self.df_mensuelles_consolidé.merge(
                temp_df, on='year_month', how='outer', suffixes=('', '_new')
            )
            
            for col in ['loyer_base_total', 'loyer_idx_total', 'loyer_irl_total', 'charges_total', 'total_brut', 'total_net', 'frais_gli_total']:
                self.df_mensuelles_consolidé[col] = (
                    self.df_mensuelles_consolidé[col].fillna(0) + 
                    self.df_mensuelles_consolidé[f'{col}_new'].fillna(0)
                )
                if f'{col}_new' in self.df_mensuelles_consolidé.columns:
                    self.df_mensuelles_consolidé.drop(f'{col}_new', axis=1, inplace=True)
    
    def _calc_facteur_index(self, loyer: Dict[str, Any], year: int, month: int) -> float:
        """
        Calcule le facteur d'indexation personnalisé pour une année/mois donné.
        Supporte les modes 'january' et 'anniversary'.
        """
        indx_freqy = loyer.get('freq_idx', 0)
        indx_tx = loyer.get('tx_idx', 0.0) / 100  # Convertir en décimal
        date_idx_mode = loyer.get('date_idx_mode', 'january')  # Par défaut janvier
        
        if indx_freqy <= 0 or indx_tx <= 0:
            return 1.0  # Pas d'indexation
        
        start_date = pd.to_datetime(loyer.get('start_date'))
        
        if date_idx_mode == 'january':
            # Mode 1er janvier - code inchangé
            annees_ecoulees = year - start_date.year
            
            if annees_ecoulees < indx_freqy:
                return 1.0
            
            if month == 1:  
                if annees_ecoulees % indx_freqy == 0:
                    nb_indexations = annees_ecoulees // indx_freqy
                else:
                    nb_indexations = annees_ecoulees // indx_freqy
            else:
                if annees_ecoulees % indx_freqy == 0 and annees_ecoulees >= indx_freqy:
                    nb_indexations = annees_ecoulees // indx_freqy
                else:
                    nb_indexations = annees_ecoulees // indx_freqy
                    
        else:  # Mode anniversaire
            # Calculer le nombre d'indexations appliquées jusqu'à cette date
            nb_indexations = 0
            
            for annee_test in range(start_date.year, year + 1):
                # Date anniversaire pour cette année
                try:
                    anniversaire = start_date.replace(year=annee_test)
                except ValueError:  # Cas du 29 février
                    anniversaire = start_date.replace(year=annee_test, day=28)
                
                # Vérifier si on doit appliquer l'indexation cette année
                annees_depuis_debut = annee_test - start_date.year
                
                if annees_depuis_debut > 0 and annees_depuis_debut % indx_freqy == 0:
                    # C'est une année d'indexation, vérifier si on a dépassé l'anniversaire
                    if year > annee_test:
                        # On est dans une année future, l'indexation s'applique
                        nb_indexations += 1
                    elif year == annee_test:
                        # On est dans l'année d'indexation, vérifier le mois
                        if month > anniversaire.month:
                            # On a dépassé le mois anniversaire
                            nb_indexations += 1
                        elif month == anniversaire.month:
                            # On est dans le mois anniversaire, l'indexation s'applique
                            nb_indexations += 1
        
        return (1 + indx_tx) ** max(0, nb_indexations)

    def _calc_facteur_irl(self, loyer: Dict[str, Any], year: int, month: int) -> float:
        """
        Calcule le facteur IRL pour une année/mois donné.
        Supporte les modes 'january' et 'anniversary'.
        Retourne le facteur multiplicateur (pas le montant du loyer).
        """
        tx_irl = loyer.get('tx_irl', 0.0) / 100  # Convertir en décimal
        date_irl_mode = loyer.get('date_irl_mode', 'january')  # Par défaut janvier
        
        if tx_irl <= 0:
            return 1.0  # Retourner le facteur 1 si pas d'IRL
        
        start_date = pd.to_datetime(loyer.get('start_date'))
        
        if date_irl_mode == 'january':
            # Mode 1er janvier - L'IRL s'applique au 1er janvier de chaque année
            annees_irl = year - start_date.year
            if month >= 1:  # À partir de janvier
                return (1 + tx_irl) ** max(0, annees_irl)
            else:
                return (1 + tx_irl) ** max(0, annees_irl - 1)
                
        else:  # Mode anniversaire
            # Calculer le nombre d'anniversaires passés
            annees_irl = 0
            
            for annee_test in range(start_date.year + 1, year + 1):
                try:
                    anniversaire = start_date.replace(year=annee_test)
                except ValueError:  # Cas du 29 février
                    anniversaire = start_date.replace(year=annee_test, day=28)
                
                if year > annee_test:
                    # On est dans une année future, l'indexation s'applique
                    annees_irl += 1
                elif year == annee_test:
                    # On est dans l'année d'anniversaire, vérifier le mois
                    if month > anniversaire.month:
                        # On a dépassé le mois anniversaire
                        annees_irl += 1
                    elif month == anniversaire.month:
                        # On est dans le mois anniversaire, l'indexation s'applique
                        annees_irl += 1
            
            return (1 + tx_irl) ** max(0, annees_irl)

    def _calculer_statistiques_base(self):
        """
        Calcule diverses statistiques sur les revenus locatifs.
        Les stats mensuelles et annuelles sont calculées à partir des loyers mensuels,
        PAS à partir des sommes quotidiennes pour éviter les variations dues au nombre de jours.
        """
        df_stats_mensuelles = self.df_mensuelles_consolidé.copy()
        df_stats_mensuelles['year'] = df_stats_mensuelles['year_month'].str[:4].astype(int)
        
        stats_annuelles = df_stats_mensuelles.groupby('year').agg({
            'loyer_base_total': 'sum',
            'loyer_idx_total': 'sum',
            'loyer_irl_total': 'sum',
            'charges_total': 'sum',
            'total_brut': 'sum',
            'total_net': 'sum',
            'frais_gli_total': 'sum'
        }).reset_index()
        
        total_loyers_base = float(df_stats_mensuelles['loyer_base_total'].sum())
        total_loyers_idx = float(df_stats_mensuelles['loyer_idx_total'].sum())
        total_loyers_irl = float(df_stats_mensuelles['loyer_irl_total'].sum())
        total_charges = float(df_stats_mensuelles['charges_total'].sum())
        total_brut = float(df_stats_mensuelles['total_brut'].sum())
        total_net = float(df_stats_mensuelles['total_net'].sum())
        total_frais_gli = float(df_stats_mensuelles['frais_gli_total'].sum())
        
        self.results = {
            'total_loyers_base': total_loyers_base,      # Loyers de base sans indexation
            'total_loyers_idx': total_loyers_idx,        # Loyers avec indexation personnalisée
            'total_loyers_irl': total_loyers_irl,        # Loyers avec IRL
            'total_charges': total_charges,
            'total_brut': total_brut,                    # Total brut (loyer_idx + charges)
            'total_net': total_net,                      # Total net (après GLI)
            'total_frais_gli': total_frais_gli,
            'nb_baux': len(self.loyers),
            'df_annuelles': stats_annuelles,
            'df_mensuelles_consolidé': self.df_mensuelles_consolidé,
            'df_mensuelles_détaillés': self.df_mensuelles_détaillés,
            'loyers_individuels': self.results_par_loyer,
        }
    
    def _stocker_resultats(self):
        """
        Stocke tous les résultats dans le ResultStore.
        """
        if not self.results:
            return
            
        self.result_store.set("loyers_results", self.results)
        
        self.result_store.set("nb_baux", self.results.get('nb_baux'))
        
        self.result_store.set("total_loyers_base", self.results.get('total_loyers_base'))
        self.result_store.set("total_loyers_idx", self.results.get('total_loyers_idx'))
        self.result_store.set("total_loyers_irl", self.results.get('total_loyers_irl'))
        self.result_store.set("total_charges", self.results.get('total_charges'))
        self.result_store.set("total_brut", self.results.get('total_brut'))
        self.result_store.set("total_net", self.results.get('total_net'))
        self.result_store.set("total_frais_gli", self.results.get('total_frais_gli'))
        
        self.result_store.set("df_annuelles", self.results.get('df_annuelles'))
        self.result_store.set("df_mensuelles_consolidé", self.results.get('df_mensuelles_consolidé'))
        self.result_store.set("df_mensuelles_détaillés", self.results.get('df_mensuelles_détaillés'))

        self.result_store.set("loyers_individuels", self.results.get('loyers_individuels'))