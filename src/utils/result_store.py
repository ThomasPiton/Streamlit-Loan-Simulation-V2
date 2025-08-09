from typing import Any, Dict

class ResultStore:
    """
    Store global thread-safe pour stocker et récupérer les résultats de calculs.
    
    Cette classe utilise des méthodes de classe pour maintenir un store global
    partagé entre toutes les instances. Elle permet de stocker les résultats
    des différents modules de calcul et de les récupérer depuis n'importe où
    dans l'application.
    
    Attributes:
        _data (Dict[str, Any]): Dictionnaire interne pour stocker les données
    """
    
    _data: Dict[str, Any] = {}

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """
        Stocke une valeur avec une clé donnée.
        
        Args:
            key (str): Clé unique pour identifier la valeur
            value (Any): Valeur à stocker (peut être de n'importe quel type)
        
        Example:
            ResultStore.set("loyer_mensuel", 1200.50)
            ResultStore.set("charges", {"eau": 30, "electricite": 60})
        """
        cls._data[key] = value

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur par sa clé.
        
        Args:
            key (str): Clé de la valeur à récupérer
            default (Any, optional): Valeur par défaut si la clé n'existe pas. Defaults to None.
        
        Returns:
            Any: La valeur stockée ou la valeur par défaut si la clé n'existe pas
        
        Example:
            loyer = ResultStore.get("loyer_mensuel")
            charges = ResultStore.get("charges", {})
        """
        return cls._data.get(key, default)

    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """
        Récupère tous les résultats stockés.
        
        Returns:
            Dict[str, Any]: Copie de tous les données stockées
        
        Note:
            Retourne une copie pour éviter les modifications accidentelles
            du store interne.
        
        Example:
            all_results = ResultStore.get_all()
            print(f"Tous les résultats: {all_results}")
        """
        return cls._data.copy()

    @classmethod
    def clear(cls) -> None:
        """
        Vide complètement le store.
        
        Supprime toutes les données stockées. Utile pour les tests
        ou pour réinitialiser l'état entre différents calculs.
        
        Example:
            ResultStore.clear()  # Remet le store à zéro
        """
        cls._data.clear()
