import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.display.base import DisplayBase

class DisplayTotalLoyer(DisplayBase):
    
    def __init__(self):
        super().__init__()
        
    def render(self):
        # Récupérer les données depuis le result_store
        total_loyers_base = self.result.get("total_loyers_base", 0)
        total_loyers_idx = self.result.get("total_loyers_idx", 0)
        total_loyers_irl = self.result.get("total_loyers_irl", 0)
        total_charges = self.result.get("total_charges", 0)
        total_brut = self.result.get("total_brut", 0)
        total_net = self.result.get("total_net", 0)
        total_frais_gli = self.result.get("total_frais_gli", 0)
        
        df_annuelles = self.result.get("df_annuelles")
        df_mensuelles_consolidé = self.result.get("df_mensuelles_consolidé")
        df_mensuelles_détaillés = self.result.get("df_mensuelles_détaillés")
        
        # Expander principal pour tous les résultats
        with st.expander("Voir le loyer consolidé", expanded=False):
            
            # === RÉSUMÉ GLOBAL ===
            st.write("## Résumé financier global")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total NET", f"{self._format_number(total_net)} €")
                st.metric("Total des charges", f"{self._format_number(total_charges)} €")
                
            with col2:
                st.metric("Total BRUT", f"{self._format_number(total_brut)} €")
                st.metric("Total frais GLI", f"{self._format_number(total_frais_gli)} €")
                
            with col3:
                rentabilite = ((total_net / total_brut) * 100) if total_brut > 0 else 0
                st.metric("Rentabilité nette", f"{rentabilite:.1f} %")
                ecart_gli = total_brut - total_net
                st.metric("Impact GLI", f"{self._format_number(ecart_gli)} €")
            
            st.divider()
            
            # === COMPARAISON DES INDEXATIONS ===
            st.write("## Comparaison des types de loyers")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Loyers de base (total)", 
                    f"{self._format_number(total_loyers_base)} €"
                )
                
            with col2:
                difference_idx = total_loyers_idx - total_loyers_base
                pourcentage_idx = ((difference_idx / total_loyers_base) * 100) if total_loyers_base > 0 else 0
                st.metric(
                    "Loyers indexés (total)", 
                    f"{self._format_number(total_loyers_idx)} €",
                    delta=f"{difference_idx:+,.0f} € ({pourcentage_idx:+.1f}%)"
                )
                
            with col3:
                difference_irl = total_loyers_irl - total_loyers_base
                pourcentage_irl = ((difference_irl / total_loyers_base) * 100) if total_loyers_base > 0 else 0
                st.metric(
                    "Loyers IRL (total)", 
                    f"{self._format_number(total_loyers_irl)} €",
                    delta=f"{difference_irl:+,.0f} € ({pourcentage_irl:+.1f}%)"
                )
            
            st.divider()
            
            # === GRAPHIQUES ===
            if df_mensuelles_consolidé is not None and not df_mensuelles_consolidé.empty:

                
                col1_graph, col2_graph = st.columns(2)
                
                with col1_graph:
                    # Graphique 1: Évolution des loyers consolidés (lignes)
                    fig_evolution = go.Figure()
                    
                    fig_evolution.add_trace(go.Scatter(
                        x=df_mensuelles_consolidé['year_month'],
                        y=df_mensuelles_consolidé['loyer_base_total'],
                        mode='lines',
                        name='Loyers base',
                        line=dict(color='#1f77b4', width=2)
                    ))
                    
                    fig_evolution.add_trace(go.Scatter(
                        x=df_mensuelles_consolidé['year_month'],
                        y=df_mensuelles_consolidé['loyer_idx_total'],
                        mode='lines',
                        name='Loyers indexés',
                        line=dict(color='#ff7f0e', width=2)
                    ))
                    
                    fig_evolution.add_trace(go.Scatter(
                        x=df_mensuelles_consolidé['year_month'],
                        y=df_mensuelles_consolidé['loyer_irl_total'],
                        mode='lines',
                        name='Loyers IRL',
                        line=dict(color='#2ca02c', width=2)
                    ))
                    
                    fig_evolution.update_layout(
                        title="Évolution des loyers totaux",
                        xaxis_title="Période",
                        yaxis_title="Montant (€)",
                        hovermode='x unified',
                        height=400
                    )
                    
                    st.plotly_chart(fig_evolution, use_container_width=True, key="chart_evolution_totaux")
                
                with col2_graph:
                    # Graphique 2: Répartition mensuelle totale (Barres empilées)
                    fig_repartition = go.Figure()
                    
                    fig_repartition.add_trace(go.Bar(
                        x=df_mensuelles_consolidé['year_month'],
                        y=df_mensuelles_consolidé['loyer_idx_total'],
                        name='Loyers indexés',
                        marker_color='#1f77b4'
                    ))
                    
                    fig_repartition.add_trace(go.Bar(
                        x=df_mensuelles_consolidé['year_month'],
                        y=df_mensuelles_consolidé['charges_total'],
                        name='Charges',
                        marker_color='#ff7f0e'
                    ))
                    
                    fig_repartition.add_trace(go.Bar(
                        x=df_mensuelles_consolidé['year_month'],
                        y=-df_mensuelles_consolidé['frais_gli_total'],
                        name='Frais GLI (déduction)',
                        marker_color='#d62728'
                    ))
                    
                    fig_repartition.update_layout(
                        title="Répartition mensuelle totale",
                        xaxis_title="Période",
                        yaxis_title="Montant (€)",
                        barmode='relative',
                        hovermode='x unified',
                        height=400
                    )
                    
                    st.plotly_chart(fig_repartition, use_container_width=True, key="chart_repartition_totaux")
                
                st.divider()
            
            # === MOYENNES ===
            if df_mensuelles_consolidé is not None and not df_mensuelles_consolidé.empty:
                nb_mois = len(df_mensuelles_consolidé)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    moy_loyers = total_loyers_idx / nb_mois if nb_mois > 0 else 0
                    st.metric("Loyers indexés/mois", f"{self._format_number(moy_loyers)} €")
                    
                with col2:
                    moy_charges = total_charges / nb_mois if nb_mois > 0 else 0
                    st.metric("Charges/mois", f"{self._format_number(moy_charges)} €")
                    
                with col3:
                    moy_brut = total_brut / nb_mois if nb_mois > 0 else 0
                    st.metric("Revenus bruts/mois", f"{self._format_number(moy_brut)} €")
                    
                with col4:
                    moy_net = total_net / nb_mois if nb_mois > 0 else 0
                    st.metric("Revenus nets/mois", f"{self._format_number(moy_net)} €")
                
                st.divider()
            

            
            # Tableau annuel
            if df_annuelles is not None and not df_annuelles.empty:
                with st.expander("Résumé annuel", expanded=False):
                    
                    df_display = df_annuelles.copy()
                    
                    # Renommer les colonnes
                    colonnes_mapping = {
                        'year': 'Année',
                        'loyer_base_total': 'Loyers base',
                        'loyer_idx_total': 'Loyers indexés', 
                        'loyer_irl_total': 'Loyers IRL',
                        'charges_total': 'Charges',
                        'total_brut': 'Total brut',
                        'total_net': 'Total net',
                        'frais_gli_total': 'Frais GLI'
                    }
                    
                    # Sélectionner et renommer les colonnes existantes
                    colonnes_existantes = [col for col in colonnes_mapping.keys() if col in df_display.columns]
                    df_display = df_display[colonnes_existantes].rename(columns=colonnes_mapping)
                    
                    # Formater les nombres (sauf la colonne Année)
                    for col in df_display.columns:
                        if col != 'Année':
                            df_display[col] = df_display[col].apply(
                                lambda x: f"{x:,.0f} €" if pd.notnull(x) else "0 €"
                            )
                    
                    st.dataframe(df_display, use_container_width=True)
            
            # Tableau mensuel consolidé
            if df_mensuelles_consolidé is not None and not df_mensuelles_consolidé.empty:
                with st.expander("Résumé mensuel", expanded=False):
                    
                    df_display = df_mensuelles_consolidé.copy()
                    
                    # Renommer les colonnes
                    colonnes_mapping = {
                        'year_month': 'Période',
                        'loyer_base_total': 'Loyers base',
                        'loyer_idx_total': 'Loyers indexés', 
                        'loyer_irl_total': 'Loyers IRL',
                        'charges_total': 'Charges',
                        'total_brut': 'Total brut',
                        'total_net': 'Total net',
                        'frais_gli_total': 'Frais GLI'
                    }
                    
                    # Sélectionner et renommer les colonnes existantes
                    colonnes_existantes = [col for col in colonnes_mapping.keys() if col in df_display.columns]
                    df_display = df_display[colonnes_existantes].rename(columns=colonnes_mapping)
                    
                    # Formater les nombres (sauf la colonne Période)
                    for col in df_display.columns:
                        if col != 'Période':
                            df_display[col] = df_display[col].apply(
                                lambda x: f"{x:,.0f} €" if pd.notnull(x) else "0 €"
                            )
                    
                    st.dataframe(df_display, use_container_width=True)
    
    def _format_number(self, value, decimals=0):
        """Formate un nombre pour l'affichage."""
        if value is None:
            return "0"
        try:
            if decimals == 0:
                return f"{float(value):,.0f}"
            else:
                return f"{float(value):,.{decimals}f}"
        except (ValueError, TypeError):
            return "0"

class DisplayLoyerIndividuel(DisplayBase):
    
    def __init__(self):
        super().__init__()
        self.loyers_individuels = self.result.get("loyers_results", {}).get("loyers_individuels", {})
        
    def render(self):
        if not self.loyers_individuels:
            st.warning("Aucun loyer trouvé dans les résultats de simulation.")
            return
        
        # Un seul expander contenant tous les loyers
        with st.expander("Voir les détails des loyers individuels", expanded=False):
            
            # Créer les tabs à l'intérieur de l'expander
            labels_loyers = list(self.loyers_individuels.keys())
            onglets = st.tabs(labels_loyers)
            
            # Afficher le contenu de chaque onglet
            for i, (label_loyer, onglet) in enumerate(zip(labels_loyers, onglets)):
                with onglet:
                    self._afficher_loyer_individuel(label_loyer, self.loyers_individuels[label_loyer], i)
    
    def _format_date(self, date_value):
        """Convertit une date en string pour Streamlit."""
        if date_value is None:
            return "N/A"
        if hasattr(date_value, 'strftime'):
            return date_value.strftime('%Y-%m-%d')
        return str(date_value)
    
    def _format_number(self, value, decimals=0):
        """Formate un nombre pour l'affichage."""
        if value is None:
            return "0"
        try:
            if decimals == 0:
                return f"{float(value):,.0f}"
            else:
                return f"{float(value):,.{decimals}f}"
        except (ValueError, TypeError):
            return "0"
    
    def _format_percentage(self, value, decimals=1):
        """Formate un pourcentage pour l'affichage."""
        if value is None:
            return "0.0"
        try:
            return f"{float(value):,.{decimals}f}"
        except (ValueError, TypeError):
            return "0.0"
    
    def _afficher_loyer_individuel(self, label: str, data_loyer: dict, index: int):
        """Affiche les détails d'un loyer individuel."""
        
        st.subheader(f"{label}")
        
        # === INFORMATIONS GÉNÉRALES ===
        st.write("**Informations générales**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Loyer mensuel de base", f"{self._format_number(data_loyer.get('loyer_mensuel_base', 0))} €")
            st.metric("Date de début", self._format_date(data_loyer.get('start_date')))
            
        with col2:
            st.metric("Charges mensuelles", f"{self._format_number(data_loyer.get('charges_mensuelles_base', 0))} €")
            st.metric("Date de fin", self._format_date(data_loyer.get('end_date')))
            
        with col3:
            nb_mois = data_loyer.get('nb_mois', 1)
            total_net = data_loyer.get('total_net', 0)
            st.metric("Nombre de mois", str(nb_mois))
            st.metric("Total net", f"{self._format_number(total_net)} €")
        
        st.divider()
        
        # === COMPARAISON DES TYPES DE LOYERS ===
        st.write("**Comparaison des indexations**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_base = data_loyer.get('total_loyers_base', 0)
        total_idx = data_loyer.get('total_loyers_idx', 0)
        total_irl = data_loyer.get('total_loyers_irl', 0)
        
        with col1:
            st.metric(
                "Loyer de base (total)", 
                f"{self._format_number(total_base)} €"
            )
            
        with col2:
            difference_idx = total_idx - total_base
            st.metric(
                "Loyer indexé (total)", 
                f"{self._format_number(total_idx)} €",
                delta=f"{difference_idx:+,.0f} €" if difference_idx != 0 else None
            )
            
        with col3:
            difference_irl = total_irl - total_base
            st.metric(
                "Loyer IRL (total)", 
                f"{self._format_number(total_irl)} €",
                delta=f"{difference_irl:+,.0f} €" if difference_irl != 0 else None
            )
            
        with col4:
            st.metric(
                "Charges (total)", 
                f"{self._format_number(data_loyer.get('total_charges', 0))} €"
            )
        
        st.divider()
        
        # === GRAPHIQUES CÔTE À CÔTE ===
        df_mensuel = data_loyer.get('df_mensuel')
        if df_mensuel is not None and not df_mensuel.empty:
            
            st.write("**Évolution mensuelle**")
            
            col1_graph, col2_graph = st.columns(2)
            
            with col1_graph:
                # Graphique 1: Évolution des loyers (lignes sans points)
                fig_loyers = go.Figure()
                
                fig_loyers.add_trace(go.Scatter(
                    x=df_mensuel['year_month'],
                    y=df_mensuel['loyer'],
                    mode='lines',
                    name='Loyer de base',
                    line=dict(color='#1f77b4', width=2)
                ))
                
                fig_loyers.add_trace(go.Scatter(
                    x=df_mensuel['year_month'],
                    y=df_mensuel['loyer_idx'],
                    mode='lines',
                    name='Loyer indexé',
                    line=dict(color='#ff7f0e', width=2)
                ))
                
                fig_loyers.add_trace(go.Scatter(
                    x=df_mensuel['year_month'],
                    y=df_mensuel['loyer_irl'],
                    mode='lines',
                    name='Loyer IRL',
                    line=dict(color='#2ca02c', width=2)
                ))
                
                fig_loyers.update_layout(
                    title="Évolution des loyers",
                    xaxis_title="Période",
                    yaxis_title="Montant (€)",
                    hovermode='x unified',
                    height=400
                )
                
                # Clé unique pour chaque graphique
                st.plotly_chart(fig_loyers, use_container_width=True, key=f"chart_loyers_{index}")
            
            with col2_graph:
                # Graphique 2: Répartition mensuelle (Loyer + Charges + GLI)
                fig_repartition = go.Figure()
                
                fig_repartition.add_trace(go.Bar(
                    x=df_mensuel['year_month'],
                    y=df_mensuel['loyer_idx'],
                    name='Loyer indexé',
                    marker_color='#1f77b4'
                ))
                
                fig_repartition.add_trace(go.Bar(
                    x=df_mensuel['year_month'],
                    y=df_mensuel['charges'],
                    name='Charges',
                    marker_color='#ff7f0e'
                ))
                
                fig_repartition.add_trace(go.Bar(
                    x=df_mensuel['year_month'],
                    y=-df_mensuel['frais_gli'],
                    name='Frais GLI (déduction)',
                    marker_color='#d62728'
                ))
                
                fig_repartition.update_layout(
                    title="Répartition mensuelle",
                    xaxis_title="Période",
                    yaxis_title="Montant (€)",
                    barmode='relative',
                    hovermode='x unified',
                    height=400
                )
                
                # Clé unique pour chaque graphique
                st.plotly_chart(fig_repartition, use_container_width=True, key=f"chart_repartition_{index}")
            
            st.divider()
        
        # === MOYENNES MENSUELLES ===
        st.write("**Moyennes mensuelles**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Loyer base/mois", f"{self._format_number(data_loyer.get('loyer_base_mensuel_moyen', 0))} €")
            
        with col2:
            st.metric("Loyer indexé/mois", f"{self._format_number(data_loyer.get('loyer_idx_mensuel_moyen', 0))} €")
            
        with col3:
            st.metric("Loyer IRL/mois", f"{self._format_number(data_loyer.get('loyer_irl_mensuel_moyen', 0))} €")
        
        st.divider()
        
        # === TABLEAU DE DONNÉES ANNUEL EXPANDABLE ===
        df_annuel = data_loyer.get('df_annuel')
        if df_annuel is not None and not df_annuel.empty:
            
            with st.expander("📊 Voir le tableau des annuités", expanded=False):
                
                # Formater le DataFrame pour l'affichage
                df_display = df_annuel.copy()
                
                # Renommer les colonnes pour un meilleur affichage
                colonnes_mapping = {
                    'year': 'Année',
                    'loyer': 'Loyer de base',
                    'loyer_idx': 'Loyer indexé', 
                    'loyer_irl': 'Loyer IRL',
                    'charges': 'Charges',
                    'total': 'Total brut',
                    'net_total': 'Total net',
                    'frais_gli': 'Frais GLI'
                }
                
                df_display = df_display.rename(columns=colonnes_mapping)
                
                # Formater les nombres
                for col in df_display.columns:
                    if col != 'Année':
                        df_display[col] = df_display[col].apply(lambda x: f"{x:,.0f} €")
                
                st.dataframe(df_display, use_container_width=True)
        
        if df_mensuel is not None and not df_mensuel.empty:
            
            with st.expander("📋 Voir le tableau des mensualités", expanded=False):
                
                # Préparer le DataFrame pour l'affichage
                colonnes_a_afficher = ['year_month', 'loyer', 'loyer_idx', 'loyer_irl', 'charges', 'total', 'frais_gli']
                
                # Vérifier quelles colonnes existent
                colonnes_existantes = [col for col in colonnes_a_afficher if col in df_mensuel.columns]
                
                if colonnes_existantes:
                    df_detail = df_mensuel[colonnes_existantes].copy()
                    
                    # Renommer les colonnes
                    colonnes_detail = {
                        'year_month': 'Période',
                        'loyer': 'Loyer base',
                        'loyer_idx': 'Loyer indexé',
                        'loyer_irl': 'Loyer IRL', 
                        'charges': 'Charges',
                        'total': 'Total brut',
                        'frais_gli': 'GLI'
                    }
                    
                    df_detail = df_detail.rename(columns=colonnes_detail)
                    
                    # Formater les colonnes monétaires
                    for col in df_detail.columns:
                        if col != 'Période':
                            df_detail[col] = df_detail[col].apply(lambda x: f"{x:,.0f} €" if pd.notnull(x) else "0 €")
                    
                    st.dataframe(df_detail, use_container_width=True)
                else:
                    st.info("Pas de détails mensuels disponibles pour ce loyer.")
                    
