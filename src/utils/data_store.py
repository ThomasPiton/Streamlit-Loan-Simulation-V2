from typing import Any, Dict

class DataStore:
    """
    Store global pour gérer les données d'entrée de l'application.
    
    Cette classe utilise des méthodes de classe pour maintenir un store global
    partagé contenant toutes les données nécessaires aux calculs. Elle sert
    de source de données centralisée pour tous les modules de compute.
    
    Attributes:
        _data (Dict[str, Any]): Dictionnaire principal pour stocker les données d'entrée
        _result (Dict[str, Any]): Dictionnaire pour les résultats (legacy, non utilisé)
    """
    
    _data: Dict[str, Any] = {}
    _result: Dict[str, Any] = {}

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """
        Stocke une donnée d'entrée avec une clé donnée.
        
        Args:
            key (str): Clé unique pour identifier la donnée
            value (Any): Valeur à stocker (peut être de n'importe quel type)
        
        Example:
            DataStore.set("prix_achat", 250000)
            DataStore.set("taux_pret", 0.025)
            DataStore.set("caracteristiques", {"surface": 80, "pieces": 3})
        """
        cls._data[key] = value

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Récupère une donnée par sa clé.
        
        Args:
            key (str): Clé de la donnée à récupérer
            default (Any, optional): Valeur par défaut si la clé n'existe pas. Defaults to None.
        
        Returns:
            Any: La valeur stockée ou la valeur par défaut si la clé n'existe pas
        
        Example:
            prix = DataStore.get("prix_achat")
            surface = DataStore.get("surface", 0)
        """
        return cls._data.get(key, default)

    @classmethod
    def all(cls) -> Dict[str, Any]:
        """
        Récupère toutes les données (référence directe).
        
        Returns:
            Dict[str, Any]: Référence directe au dictionnaire interne
        
        Warning:
            Cette méthode retourne une référence directe aux données internes.
            Les modifications affecteront directement le store.
            Préférer get_all() pour une utilisation sûre.
        
        Example:
            data_ref = DataStore.all()  # Référence directe
        """
        return cls._data
    
    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """
        Récupère toutes les données (copie sécurisée).
        
        Returns:
            Dict[str, Any]: Copie de toutes les données stockées
        
        Note:
            Retourne une copie pour éviter les modifications accidentelles
            du store interne. C'est la méthode recommandée pour récupérer
            toutes les données.
        
        Example:
            all_data = DataStore.get_all()
            print(f"Toutes les données: {all_data}")
        """
        return cls._data.copy()
