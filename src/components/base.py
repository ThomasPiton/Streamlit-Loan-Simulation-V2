from abc import ABC, abstractmethod

class BaseComponent(ABC):
    
    def __init__(self):
        pass

    @abstractmethod
    def render(self):
        """
        Méthode à implémenter dans chaque section pour afficher les composants Streamlit.
        """
        pass
    
    @abstractmethod
    def validate(self):
        """
        Méthode à implémenter dans chaque section pour afficher les composants Streamlit.
        """
        pass
    
    @abstractmethod
    def store(self):
        """
        Méthode à implémenter dans chaque section pour afficher les composants Streamlit.
        """
        pass
    
    