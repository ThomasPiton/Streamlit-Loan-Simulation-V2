import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Any, Optional
import calendar

from ..src.utils.result_store import ResultStore
from ..src.calc.base_compute import BaseCompute
from .config import get_sample_loyers

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
        
        self.loyers = get_sample_loyers()
        
        self.results = {}
        self.result_store = ResultStore()
        
        self._get_simulation_dates()
        self._init_df()
    
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
            self._calculer_loyer_standard(loyer)
            
        self._calculer_totaux_quotidiens()
        
        self._calculer_statistiques_loyers()
        
        self._stocker_resultats()
    
    def _calculer_loyer_mensuel(self):
        """
        Calcule les stats mensuelles optimisées directement depuis les contrats.
        Retourne aussi le détail par loyer pour chaque mensualité.
        """
        # Générer toutes les mensualités de la période
        date_courante = self.start_date.replace(day=1)
        date_fin = self.end_date.replace(day=1)
        
        stats_mensuelles = []
        stats_mensuelles_detaillees = []
        
        while date_courante <= date_fin:
            year = date_courante.year
            month = date_courante.month
            year_month = date_courante.strftime('%Y-%m')
            
            loyer_total_mois = 0.0
            charges_total_mois = 0.0
            
            # Traiter chaque contrat pour ce mois
            for loyer in self.loyers:
                label = loyer.get('label', 'Loyer sans nom')
                start_date = pd.to_datetime(loyer.get('start_date')).date()
                end_date = pd.to_datetime(loyer.get('end_date')).date()
                
                # Vérifier si ce mois est dans la période du contrat
                if start_date <= date_courante <= end_date:
                    taux_occupation = loyer.get('taux_occupation', 100) / 100
                    loyer_mensuel = loyer.get('loyer_mensuel', 0) * taux_occupation
                    charges_mensuelles = loyer.get('charges_mensuelles', 0) * taux_occupation
                    
                    # Appliquer l'indexation si nécessaire
                    if loyer.get('tx_idx', False):
                        facteur_indexation = self._calculer_facteur_indexation(loyer, year, month)
                        loyer_mensuel *= facteur_indexation
                        charges_mensuelles *= facteur_indexation
                    
                    loyer_total_mois += loyer_mensuel
                    charges_total_mois += charges_mensuelles
                    
                    # Ajouter le détail pour ce loyer spécifique
                    stats_mensuelles_detaillees.append({
                        'year_month': year_month,
                        'label': label,
                        'loyer_mensuel': float(loyer_mensuel),
                        'charges_mensuelles': float(charges_mensuelles),
                        'taux_occupation': float(loyer.get('taux_occupation', 100)),
                        'indexation_appliquee': float(facteur_indexation if loyer.get('indexation', False) else 1.0)
                    })
            
            # Ajouter les totaux mensuels
            stats_mensuelles.append({
                'year_month': year_month,
                'loyer_total': float(loyer_total_mois),
                'charges_total': float(charges_total_mois)
            })
            
            date_courante += relativedelta(months=1)
        
        self.df_stats_mensuelles = pd.DataFrame(stats_mensuelles)
        self.df_stats_mensuelles_detaillees = pd.DataFrame(stats_mensuelles_detaillees)

    def _calculer_loyer_standard(self, loyer: Dict[str, Any]):
        """
        Calcule les revenus quotidiens pour un contrat de location (mode standard).
        """
        label = loyer.get('label', 'Loyer sans nom')
        start_date = pd.to_datetime(loyer.get('start_date')).date()
        end_date = pd.to_datetime(loyer.get('end_date')).date()
        
        loyer_mensuel_base = loyer.get('loyer_mensuel', 0)
        charges_mensuelles_base = loyer.get('charges_mensuelles', 0)
        taux_occupation = loyer.get('taux_occupation', 100) / 100
        tx_gli = loyer.get('tx_gli', 0.0) / 100
        tx_idx = loyer.get('tx_idx', 0.0) / 100
        tx_irl = loyer.get('tx_irl', 0.0) / 100
        freq_idx = loyer.get('freq_idx', 0)
        
        # Filtrer sur la période du contrat
        mask_periode = (self.df_dates['date'] >= pd.to_datetime(start_date)) & \
                       (self.df_dates['date'] <= pd.to_datetime(end_date))
        
        if not mask_periode.any():
            return
        
        # Créer des colonnes pour ce loyer spécifique
        col_loyer = f'loyer_{label.replace(" ", "_")}'
        col_charges = f'charges_{label.replace(" ", "_")}'
        col_total = f'total_{label.replace(" ", "_")}'
        col_net_total = f'net_total_{label.replace(" ", "_")}'
        col_frais_gli = f'frais_gli_{label.replace(" ", "_")}'
        col_loyer_idx = f'loyer_idx_{label.replace(" ", "_")}'
        col_loyer_irl = f'loyer_irl_{label.replace(" ", "_")}'
        col_frais_gli = f'frais_gli_{label.replace(" ", "_")}'
        
        # Initialiser les colonnes
        self.df_loyers[col_loyer] = 0.0
        self.df_loyers[col_charges] = 0.0
        self.df_loyers[col_total] = 0.0
        self.df_loyers[col_net_total] = 0.0
        self.df_loyers[col_loyer_idx] = 0.0
        self.df_loyers[col_loyer_irl] = 0.0
        self.df_loyers[col_frais_gli] = 0.0
        
        # Appliquer les calculs pour chaque jour de la période
        for idx in self.df_loyers[mask_periode].index:
            
            row_date = self.df_loyers.loc[idx, 'date'].date()
            year = row_date.year
            month = row_date.month
            
            # Calculer les facteurs
            facteurs = self._calculer_facteurs_indexation(loyer, year, month)
            
            # Calculs mensuels
            loyer_mensuel = loyer_mensuel_base * facteurs['indexation'] * taux_occupation
            loyer_mensuel_idx = loyer_mensuel_base * facteurs['indexation'] * taux_occupation
            loyer_mensuel_irl = facteurs['irl'] * taux_occupation
            
            charges_mensuelles = charges_mensuelles_base * taux_occupation
            total_mensuelles = loyer_mensuel + charges_mensuelles
            frais_gli_mensuel = total_mensuelles * tx_gli
            net_total_mensuel = total_mensuelles - frais_gli_mensuel
            
            # Répartir sur les jours du mois
            jours_dans_mois = calendar.monthrange(year, month)[1]
            
            # Stocker les valeurs quotidiennes
            self.df_loyers.loc[idx, col_loyer] = loyer_mensuel / jours_dans_mois
            self.df_loyers.loc[idx, col_charges] = charges_mensuelles / jours_dans_mois
            self.df_loyers.loc[idx, col_total] = net_total_mensuel / jours_dans_mois
            self.df_loyers.loc[idx, col_net_total] = net_total_mensuel / jours_dans_mois
            self.df_loyers.loc[idx, col_loyer_idx] = loyer_mensuel_idx / jours_dans_mois
            self.df_loyers.loc[idx, col_loyer_irl] = loyer_mensuel_irl / jours_dans_mois
            self.df_loyers.loc[idx, col_frais_gli] = frais_gli_mensuel / jours_dans_mois
    
    def _calculer_facteurs_indexation(self, loyer: Dict[str, Any], year: int, month: int) -> Dict[str, float]:
        facteur_indexation = self._calculer_facteur_indexation_personnalise(loyer, year, month)
        
        # Facteur IRL
        facteur_irl = self._calculer_facteur_irl(loyer, year, month)
        
        return {
            'indexation': facteur_indexation,
            'irl': facteur_irl
        }

    def _calculer_facteur_indexation_personnalise(self, loyer: Dict[str, Any], year: int, month: int) -> float:
        indx_freqy = loyer.get('freq_idx', 0)
        indx_tx = loyer.get('tx_idx', 0.0) / 100  # Convertir en décimal
        
        if indx_freqy <= 0 or indx_tx <= 0:
            return 1.0  # Pas d'indexation
        
        start_date = pd.to_datetime(loyer.get('start_date'))
        
        # Calculer le nombre d'années complètes depuis le début du contrat
        annees_ecoulees = year - start_date.year
        
        # Si on n'a pas encore atteint la première période d'indexation
        if annees_ecoulees < indx_freqy:
            return 1.0
        
        # Calculer le nombre de cycles d'indexation appliqués (seulement en janvier)
        if month == 1:  # Indexation au 1er janvier
            nb_indexations = annees_ecoulees // indx_freqy
        else:
            # Pour les autres mois, prendre l'indexation du janvier précédent
            nb_indexations = max(0, (annees_ecoulees)) // indx_freqy
            # Si on est après janvier de l'année d'indexation, appliquer l'indexation
            if annees_ecoulees >= indx_freqy and (annees_ecoulees % indx_freqy == 0):
                nb_indexations += 1
        
        return (1 + indx_tx) ** max(0, nb_indexations)

    def _calculer_facteur_irl(self, loyer: Dict[str, Any], year: int, month: int) -> float:
        """
        Calcule le facteur IRL pour une année/mois donné.
        L'IRL s'applique chaque année au 1er janvier.
        """
        tx_irl = loyer.get('tx_irl', 0.0) / 100  # Convertir en décimal
        
        if tx_irl <= 0:
            return loyer.get('loyer_mensuel', 0)  # Retourner le loyer de base si pas d'IRL
        
        start_date = pd.to_datetime(loyer.get('start_date'))
        
        # Calculer le nombre d'années depuis le début du contrat
        annees_irl = year - start_date.year
        if month < start_date.month:
            annees_irl -= 1  # Ne pas compter l'année en cours si on n'a pas atteint le mois anniversaire
        
        # Le loyer de base avec IRL cumulé
        loyer_base = loyer.get('loyer_mensuel', 0)
        return loyer_base * ((1 + tx_irl) ** max(0, annees_irl))

    def _calculer_facteur_indexation(self, loyer: Dict[str, Any], year: int, month: int) -> float:
        return self._calculer_facteur_indexation_personnalise(loyer, year, month)
    
    def _calculer_totaux_quotidiens(self):
        """
        Calcule les totaux quotidiens de loyers et charges (mode standard uniquement).
        """
        # Identifier toutes les colonnes par type
        colonnes_loyers = [col for col in self.df_loyers.columns if col.startswith('loyer_') and col != 'loyer']
        colonnes_charges = [col for col in self.df_loyers.columns if col.startswith('charges_') and col != 'charges']
        colonnes_totaux = [col for col in self.df_loyers.columns if col.startswith('total_') and col != 'total']
        colonnes_loyers_irl = [col for col in self.df_loyers.columns if col.startswith('loyer_irl_') and col != 'loyer_irl']
        colonnes_frais_gli = [col for col in self.df_loyers.columns if col.startswith('frais_gli_') and col != 'frais_gli']
        
        # Calculer les totaux quotidiens
        if colonnes_loyers:
            self.df_loyers['loyer'] = self.df_loyers[colonnes_loyers].sum(axis=1)
        if colonnes_charges:
            self.df_loyers['charges'] = self.df_loyers[colonnes_charges].sum(axis=1)
        if colonnes_totaux:
            self.df_loyers['total'] = self.df_loyers[colonnes_totaux].sum(axis=1)
        if colonnes_loyers_irl:
            self.df_loyers['loyer_irl'] = self.df_loyers[colonnes_loyers_irl].sum(axis=1)
        if colonnes_frais_gli:
            self.df_loyers['frais_gli'] = self.df_loyers[colonnes_frais_gli].sum(axis=1)
    
    def _calculer_statistiques_loyers(self):
        """
        Calcule les statistiques en mode standard.
        """
        self._calculer_statistiques_base(mode_optimise=False)
    
    def _calculer_statistiques_optimise(self):
        """
        Calcule les statistiques en mode optimisé.
        """
        self._calculer_statistiques_base(mode_optimise=True)
    
    def _calculer_statistiques_base(self, mode_optimise: bool = False):
        """
        Calcule diverses statistiques sur les revenus locatifs.
        Les stats mensuelles et annuelles sont calculées à partir des loyers mensuels,
        PAS à partir des sommes quotidiennes pour éviter les variations dues au nombre de jours.
        """
        if mode_optimise:
            # En mode optimisé, on a déjà les stats mensuelles
            df_stats_mensuelles = self.df_stats_mensuelles
        else:
            # En mode standard, on les calcule
            df_stats_mensuelles = self._calculer_stats_mensuelles_depuis_contrats()
        
        # ===== CALCULS DES STATS ANNUELLES =====
        # Extraire l'année depuis year_month pour les groupements
        df_stats_mensuelles = df_stats_mensuelles.copy()
        df_stats_mensuelles['year'] = df_stats_mensuelles['year_month'].str[:4].astype(int)
        
        # Calculer les stats annuelles
        stats_annuelles = df_stats_mensuelles.groupby('year').agg({
            'loyer': 'sum',
            'charges': 'sum',
            'total': 'sum',
            'loyer_irl': 'sum',
            'frais_gli': 'sum'
        }).reset_index()
        
        # ===== CALCULS DES TOTAUX ET MOYENNES =====
        total_loyers = float(df_stats_mensuelles['loyer'].sum())
        total_charges = float(df_stats_mensuelles['charges'].sum())
        total_net = float(df_stats_mensuelles['total'].sum())
        total_loyer_irl = float(df_stats_mensuelles['loyer_irl'].sum())
        total_frais_gli = float(df_stats_mensuelles['frais_gli'].sum())
        
        # Nombre de mois avec des loyers > 0 pour calculer les moyennes
        mois_avec_loyers = len(df_stats_mensuelles[df_stats_mensuelles['loyer'] > 0])
        nb_mois_total = len(df_stats_mensuelles)
        
        loyer_mensuel_moyen = total_loyers / max(mois_avec_loyers, 1)
        charges_mensuelles_moyennes = total_charges / max(mois_avec_loyers, 1)
        
        # ===== CALCULS PAR BAIL =====
        stats_par_bail = self._calculer_stats_par_bail()
        
        # ===== CALCULER LA DURÉE =====
        duree_jours = (self.date_fin_simulation - self.date_debut_simulation).days
        duree_mois = nb_mois_total
        
        # ===== STOCKER TOUS LES RÉSULTATS =====
        df_stats_mensuelles_clean = df_stats_mensuelles.drop('year', axis=1)
        
        self.results = {
            'df_loyers_quotidiens': self.df_loyers,
            'stats_annuelles': stats_annuelles,
            'stats_mensuelles': df_stats_mensuelles_clean,
            'total_loyers': total_loyers,
            'total_charges': total_charges,
            'total_net': total_net,
            'total_loyer_irl': total_loyer_irl,
            'total_frais_gli': total_frais_gli,
            'loyer_mensuel_moyen': loyer_mensuel_moyen,
            'charges_mensuelles_moyennes': charges_mensuelles_moyennes,
            'duree_jours': duree_jours,
            'duree_mois': duree_mois,
            'nb_baux': len(self.loyers),
            'stats_par_bail': stats_par_bail,
            'mode_optimise': mode_optimise
        }
    
    def _calculer_stats_mensuelles_depuis_contrats(self):
        """
        Version non-optimisée qui utilise la nouvelle méthode complète.
        """
        self._calculer_stats_mensuelles_complet()
        return self.df_stats_mensuelles
    
    def _calculer_stats_mensuelles_complet(self):
        """
        Calcule les statistiques mensuelles complètes à partir des contrats.
        Cette méthode est utilisée en mode standard pour avoir la même logique qu'en mode optimisé.
        """
        # Initialiser le DataFrame comme en mode optimisé
        start_month = self.date_debut_simulation.replace(day=1)
        end_month = self.date_fin_simulation.replace(day=1)
        
        months = []
        current = start_month
        while current <= end_month:
            months.append(current.strftime('%Y-%m'))
            current += relativedelta(months=1)
        
        self.df_stats_mensuelles = pd.DataFrame({
            'year_month': months,
            'loyer': 0.0,
            'charges': 0.0,
            'total': 0.0,
            'loyer_irl': 0.0,
            'frais_gli': 0.0
        })
        
        # Appliquer chaque contrat
        for loyer in self.loyers:
            self._calculer_loyer_optimise(loyer)
    
    def _calculer_stats_par_bail(self) -> List[Dict[str, Any]]:
        """
        Calcule les statistiques par bail individuel.
        """
        stats_par_bail = []
        
        for loyer in self.loyers:
            label = loyer.get('label', 'Loyer sans nom')
            start_date = pd.to_datetime(loyer.get('start_date')).date()
            end_date = pd.to_datetime(loyer.get('end_date')).date() 
            
            loyer_mensuel_base = loyer.get('loyer_mensuel', 0)
            charges_mensuelles_base = loyer.get('charges_mensuelles', 0)
            taux_occupation_display = loyer.get('taux_occupation', 100)
            taux_occupation_calc = taux_occupation_display / 100
            tx_gli = loyer.get('tx_gli', 0.0) / 100
            
            # Calculer la période d'activité en mois
            debut_mois = start_date.replace(day=1)
            fin_mois = end_date.replace(day=1)
            
            mois_actifs = 0
            total_loyer_bail = 0.0
            total_charges_bail = 0.0
            total_net_bail = 0.0
            total_loyer_irl_bail = 0.0
            total_frais_gli_bail = 0.0
            
            date_courante = debut_mois
            while date_courante <= fin_mois:
                year = date_courante.year
                month = date_courante.month
                
                # Vérifier si ce mois est dans la période du contrat
                if start_date <= date_courante <= end_date:
                    mois_actifs += 1
                    
                    # Calculer les facteurs d'indexation
                    facteurs = self._calculer_facteurs_indexation(loyer, year, month)
                    
                    loyer_mensuel = loyer_mensuel_base * facteurs['indexation'] * taux_occupation_calc
                    charges_mensuelles = charges_mensuelles_base * taux_occupation_calc
                    loyer_irl_mensuel = facteurs['irl'] * taux_occupation_calc
                    
                    # Calcul GLI
                    total_avant_gli = loyer_mensuel + charges_mensuelles
                    frais_gli_mensuel = total_avant_gli * tx_gli
                    total_net_mensuel = total_avant_gli - frais_gli_mensuel
                    
                    total_loyer_bail += loyer_mensuel
                    total_charges_bail += charges_mensuelles
                    total_net_bail += total_net_mensuel
                    total_loyer_bail += loyer_mensuel
                    total_charges_bail += charges_mensuelles
                    total_net_bail += total_net_mensuel
                    total_loyer_irl_bail += loyer_irl_mensuel
                    total_frais_gli_bail += frais_gli_mensuel
                
                date_courante += relativedelta(months=1)
            
            stats_bail = {
                'label': label,
                'loyer_total': float(total_loyer_bail),
                'charges_total': float(total_charges_bail),
                'total_net': float(total_net_bail),
                'loyer_irl_total': float(total_loyer_irl_bail),
                'frais_gli_total': float(total_frais_gli_bail),
                'debut': loyer.get('start_date'),
                'fin': loyer.get('end_date'),
                'duree_mois': mois_actifs,
                'taux_occupation': float(taux_occupation_display),
                'tx_gli': float(loyer.get('tx_gli', 0.0)),
                'indx_freqy': loyer.get('indx_freqy', 0),
                'indx_tx': float(loyer.get('indx_tx', 0.0)),
                'tx_irl': float(loyer.get('tx_irl', 0.0)),
                'loyer_mensuel_theorique': loyer_mensuel_base,
                'loyer_mensuel_effectif': float(loyer_mensuel_base * taux_occupation_calc)
            }
            stats_par_bail.append(stats_bail)
        
        return stats_par_bail

    def _stocker_resultats(self):
        """
        Stocke tous les résultats dans le ResultStore.
        """
        if not self.results:
            return
            
        # Stocker les résultats principaux
        self.result_store.set("loyers_results", self.results)
        self.result_store.set("loyers_df_quotidien", self.results.get('df_loyers_quotidiens'))
        self.result_store.set("loyers_stats_mensuelles", self.results.get('stats_mensuelles'))
        self.result_store.set("loyers_stats_annuelles", self.results.get('stats_annuelles'))
        self.result_store.set("loyers_stats_par_bail", self.results.get('stats_par_bail'))
        
        # Stocker les totaux
        self.result_store.set("loyers_total", self.results.get('total_loyers', 0))
        self.result_store.set("charges_total", self.results.get('total_charges', 0))
        self.result_store.set("loyers_net_total", self.results.get('total_net', 0))
        self.result_store.set("loyers_irl_total", self.results.get('total_loyer_irl', 0))
        self.result_store.set("frais_gli_total", self.results.get('total_frais_gli', 0))
        


if __name__ == '__main__':
    
    LoyerCompute().run()
