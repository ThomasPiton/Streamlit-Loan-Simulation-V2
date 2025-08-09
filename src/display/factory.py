from src.display.base import DisplayBase
from src.display.manager import DisplayLoyerIndividuel,DisplayTotalLoyer
import streamlit as st

class DisplayFactory:
    def __init__(self, display: str = None):
        self.display = display.upper() if display else None 

    def render(self):
        """Crée et affiche la bonne visualisation selon la valeur de display."""
        if self.display == "DISPLAY_LOYER_INDIVIDUEL":
            view = DisplayLoyerIndividuel()

        elif self.display == "DISPLAY_TOTAL_LOYER":
            view = DisplayTotalLoyer()

        elif self.display == "DISPLAY_RESULT_V2":
            pass

        elif self.display == "DISPLAY_RESULT_V3":
            pass

        elif self.display == "DISPLAY_RESULT_V4":
            pass

        elif self.display == "DISPLAY_RESULT_V5":
            pass

        else:
            raise ValueError(f"DisplayFactory: Unknown display type '{self.display}'")

        view.render()
        return view
