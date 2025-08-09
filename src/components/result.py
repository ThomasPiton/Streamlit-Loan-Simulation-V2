import streamlit as st

from src.calc.engine import EngineCompute
from src.utils.result_store import ResultStore
from src.display.factory import DisplayFactory

class Result:
    
    @staticmethod
    def render():
        
        EngineCompute().run_all()
        
        st.markdown(
            """
            <div style="
                height: 5px;
                background: linear-gradient(90deg, #262730 0%, #ff4b4b 15%, #ff6b35 35%, #f7931e 50%, #ff6b35 65%, #ff4b4b 85%, #262730 100%);
                margin: 2.5rem 0;
                border-radius: 1.5px;
                opacity: 0.8;
                box-shadow: 0 1px 3px rgba(255, 75, 75, 0.3);
            "></div>
            """, 
            unsafe_allow_html=True
        )
                                
        st.header("Overview des résultats")
        st.header("Détails des résultats")
        st.subheader("1. Résultat Loyer")
        DisplayFactory(display="DISPLAY_TOTAL_LOYER").render()
        DisplayFactory(display="DISPLAY_LOYER_INDIVIDUEL").render()
        st.subheader("2. Résultat Prêt")
        st.subheader("3. Résultat Bien")
        st.subheader("4. Résultat Travaux")
        st.subheader("5. Résultat Hypothèse")
        
        

        