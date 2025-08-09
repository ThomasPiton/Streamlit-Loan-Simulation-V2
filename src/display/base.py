from abc import ABC, abstractmethod
from src.utils.result_store import ResultStore

class DisplayBase(ABC):
    
    def __init__(self):
        self.result_store = ResultStore()
        self.result = self.result_store.get_all()

    @abstractmethod  
    def render(self):
        pass
