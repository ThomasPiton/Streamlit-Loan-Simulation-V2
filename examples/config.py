import datetime
from typing import List, Dict

def get_sample_loyers() -> List[Dict]:
    return [
        {
            "label": "Loyer 1",
            "loyer_mensuel": 1400,
            "jour_paiement": 1,
            "charges_mensuelles": 20,
            "duree_contrat_mois": 300,
            "duree_contrat_annees": 25,
            "start_date": datetime.date(2025, 8, 2),
            "end_date": datetime.date(2050, 8, 2),
            "tx_gli": 3.0,
            "freq_idx": 5,
            "tx_idx": 1.0,
            "tx_irl": 1.0,
            "taux_occupation": 90.0,
            "mois_occupes": 10.8
        },
        {
            "label": "Loyer 2",
            "loyer_mensuel": 1400,
            "jour_paiement": 1,
            "charges_mensuelles": 20,
            "duree_contrat_mois": 300,
            "duree_contrat_annees": 25,
            "start_date": datetime.date(2025, 8, 2),
            "end_date": datetime.date(2050, 8, 2),
            "tx_gli": 3.0,
            "freq_idx": 5,
            "tx_idx": 1.0,
            "tx_irl": 1.0,
            "taux_occupation": 90.0,
            "mois_occupes": 10.8
        },
        {
            "label": "Loyer 3",
            "loyer_mensuel": 1400,
            "jour_paiement": 1,
            "charges_mensuelles": 20,
            "duree_contrat_mois": 300,
            "duree_contrat_annees": 25,
            "start_date": datetime.date(2025, 8, 2),
            "end_date": datetime.date(2050, 8, 2),
            "tx_gli": 3.0,
            "freq_idx": 5,
            "tx_idx": 1.0,
            "tx_irl": 1.0,
            "taux_occupation": 90.0,
            "mois_occupes": 10.8
        },
    ]
