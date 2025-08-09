from src.calc import *

class EngineCompute:
    """
    Moteur de calcul qui exécute toutes les classes de compute définies.
    
    Cette classe centralise l'exécution de tous les calculs nécessaires
    en instanciant et exécutant chaque classe de compute dans l'ordre défini.
    """
    
    def __init__(self):
        """
        Initialise le moteur avec la liste des classes de compute à exécuter.
        
        Les classes sont exécutées dans l'ordre de définition dans la liste.
        Actuellement configuré pour :
        - PretCompute : Calculs liés aux prêts
        - LoyerCompute : Calculs liés aux loyers
        """
        self.compute_classes = [
            PretCompute,
            LoyerCompute
        ]
    
    def run_all(self):
        """
        Exécute la méthode run() de toutes les classes de compute.
        
        Pour chaque classe dans self.compute_classes :
        1. Crée une instance de la classe
        2. Appelle sa méthode run()
        3. Les résultats sont automatiquement stockés dans ResultStore
           via les méthodes store_result() de chaque compute
        
        Returns:
            None
        
        Note:
            Cette méthode ne retourne rien car les résultats sont stockés
            dans le ResultStore global accessible via ResultStore.get_all()
        """
        for compute_class in self.compute_classes:
            # Créer une instance de la classe de compute
            compute_instance = compute_class()
            
            # Exécuter tous les calculs de cette classe
            compute_instance.run()