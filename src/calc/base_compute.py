from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from src.utils.data_store import DataStore
from src.utils.result_store import ResultStore


class BaseCompute(ABC):
    """
    Classe abstraite de base pour tous les calculs (computes).
    
    Cette classe fournit une structure commune pour tous les modules de calcul
    en gérant l'accès aux données d'entrée et le stockage des résultats.
    
    Attributes:
        data (Dict[str, Any]): Toutes les données disponibles récupérées depuis DataStore
    """
    
    def __init__(self):
        """
        Initialise la classe de compute avec toutes les données disponibles.
        
        Récupère automatiquement toutes les données depuis DataStore pour
        les rendre disponibles aux classes enfants via self.data.
        """
        self.data = DataStore.get_all()

    @abstractmethod
    def run(self):
        """
        Méthode abstraite à implémenter dans chaque classe enfant.
        
        Cette méthode doit contenir toute la logique de calcul spécifique
        à chaque type de compute. Elle est appelée par EngineCompute.run_all().
        
        Les résultats doivent être stockés via self.store_result(key, value).
        
        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée dans la classe enfant
        """
        pass

    def store_result(self, key: str, value: Any) -> None:
        """
        Méthode utilitaire pour stocker des résultats dans le ResultStore global.
        
        Args:
            key (str): Clé unique pour identifier le résultat
            value (Any): Valeur du résultat à stocker (peut être de n'importe quel type)
        
        Example:
            self.store_result("loyer_mensuel", 1200.50)
            self.store_result("total_charges", {"mensuelles": 150, "annuelles": 1800})
        """
        ResultStore.set(key, value)
