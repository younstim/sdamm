#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Score CSR",
    page_icon="📊",
    layout="wide"
)

# Fonction pour charger les données
@st.cache_data
def load_data():
    try:
        # Utilisez le nom exact du fichier que vous avez dans votre dossier
        df = pd.read_csv("csr_data_200_entreprises_26indicateurs.csv")
        
        # Ajout d'une colonne Pays pour le filtre et la comparaison
        # Générer des pays aléatoires pour les entreprises
        countries = ["France", "Allemagne", "Italie", "Espagne", "Royaume-Uni", "Belgique", "Pays-Bas", "Suisse", "Portugal", "Suède"]
        df["Pays"] = np.random.choice(countries, size=len(df))
        
        return df
    except FileNotFoundError:
        st.error("Fichier CSV non trouvé. Vérifiez que le fichier est dans le même dossier que le script.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        return pd.DataFrame()

# Chargement des données
df = load_data()

if df.empty:
    st.stop()  # Arrête l'exécution si les données ne sont pas chargées

# Titre du dashboard
st.title("Dashboard de Reporting CSR")
st.markdown("### Plateforme d'analyse et de calcul de scores RSE")

# Sidebar pour les filtres
st.sidebar.header("Filtres")

# Filtre par pays
countries = ["Tous"] + sorted(df["Pays"].unique().tolist())
selected_country = st.sidebar.selectbox("Pays", countries)

# Filtre par secteur
sectors = ["Tous"] + sorted(df["Secteur"].unique().tolist())
selected_sector = st.sidebar.selectbox("Secteur", sectors)

# Filtre par taille
sizes = ["Toutes"] + sorted(df["Taille"].unique().tolist())
selected_size = st.sidebar.selectbox("Taille", sizes)

# Application des filtres
filtered_df = df.copy()
if selected_country != "Tous":
    filtered_df = filtered_df[filtered_df["Pays"] == selected_country]
if selected_sector != "Tous":
    filtered_df = filtered_df[filtered_df["Secteur"] == selected_sector]
if selected_size != "Toutes":
    filtered_df = filtered_df[filtered_df["Taille"] == selected_size]

# Création des onglets
tab1, tab2, tab3, tab4 = st.tabs(["Vue d'ensemble", "Analyse par pilier", "Comparaison d'entreprises", "Comparaison par pays"])

with tab1:
    st.header("Vue d'ensemble des scores CSR")
    
    # Métriques clés
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Score CSR Global Moyen", f"{filtered_df['Score CSR Global'].mean():.1f}/100")
    col2.metric("Score Environnement Moyen", f"{filtered_df['Score Environnement'].mean():.1f}/100")
    col3.metric("Score Social Moyen", f"{filtered_df['Score Social'].mean():.1f}/100")
    col4.metric("Score Gouvernance Moyen", f"{filtered_df['Score Gouvernance'].mean():.1f}/100")
    
    # Distribution des scores globaux
    st.subheader("Distribution des scores CSR globaux")
    fig = px.histogram(filtered_df, x="Score CSR Global", nbins=20,
                      color_discrete_sequence=["#1f77b4"])
    fig.update_layout(xaxis_title="Score CSR Global", yaxis_title="Nombre d'entreprises")
    st.plotly_chart(fig, use_container_width=True)
    
    # Top 10 des entreprises avec les meilleurs scores
    st.subheader("Top 10 des entreprises avec les meilleurs scores CSR")
    top10 = filtered_df.sort_values("Score CSR Global", ascending=False).head(10)
    fig = px.bar(top10, x="Entreprise", y="Score CSR Global", 
                color="Score CSR Global", color_continuous_scale="viridis")
    fig.update_layout(xaxis_title="Entreprise", yaxis_title="Score CSR Global")
    st.plotly_chart(fig, use_container_width=True)
    
    # Comparaison des scores par secteur
    if len(filtered_df["Secteur"].unique()) > 1:
        st.subheader("Scores CSR moyens par secteur")
        sector_scores = filtered_df.groupby("Secteur")[["Score Environnement", "Score Social", "Score Gouvernance", "Score CSR Global"]].mean().reset_index()
        fig = px.bar(sector_scores, x="Secteur", y=["Score Environnement", "Score Social", "Score Gouvernance"], 
                    barmode="group")
        fig.update_layout(xaxis_title="Secteur", yaxis_title="Score moyen")
        st.plotly_chart(fig, use_container_width=True)
    
    # Comparaison des scores par taille
    if len(filtered_df["Taille"].unique()) > 1:
        st.subheader("Scores CSR moyens par taille d'entreprise")
        size_scores = filtered_df.groupby("Taille")[["Score Environnement", "Score Social", "Score Gouvernance", "Score CSR Global"]].mean().reset_index()
        fig = px.bar(size_scores, x="Taille", y=["Score Environnement", "Score Social", "Score Gouvernance"], 
                    barmode="group", 
                    category_orders={"Taille": ["Petite", "Moyenne", "Grande"]})
        fig.update_layout(xaxis_title="Taille de l'entreprise", yaxis_title="Score moyen")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Analyse par pilier RSE")
    
    # Sélection du pilier
    pillar = st.selectbox("Sélectionner un pilier", ["Environnement", "Social", "Gouvernance"])
    
    if pillar == "Environnement":
        indicators = [col for col in df.columns if col in ["Émissions GES (tonnes CO2e)", 
                                                         "Consommation d'énergie renouvelable (%)",
                                                         "Déchets produits (tonnes)",
                                                         "Déchets recyclés (%)",
                                                         "Consommation d'eau (m³)",
                                                         "Production locale (%)"]]
        normalized_indicators = [col + " (normalisé)" for col in indicators]
    elif pillar == "Social":
        indicators = [col for col in df.columns if col in ["Nombre total de salariés", 
                                                          "Part de CDI (%)",
                                                          "Part de femmes (%)",
                                                          "Satisfaction employés (%)",
                                                          "Femmes dans postes de direction (%)",
                                                          "Salariés formés (%)",
                                                          "Index Egapro (0-100)",
                                                          "Embauches annuelles",
                                                          "Licenciements annuels",
                                                          "Taux d'absentéisme (%)",
                                                          "Réunions partenaires sociaux",
                                                          "Jours télétravaillés/salarié",
                                                          "Ancienneté >5 ans (%)"]]
        normalized_indicators = [col + " (normalisé)" for col in indicators]
    else:
        indicators = [col for col in df.columns if col in ["Écart salaires dirigeants/employés (ratio)", 
                                                          "Comité éthique (1=oui, 0=non)",
                                                          "Fournisseurs audités RSE (%)",
                                                          "Formations anti-corruption",
                                                          "Niveaux hiérarchiques",
                                                          "Budget RSE (€)",
                                                          "Taille équipe RSE"]]
        normalized_indicators = [col + " (normalisé)" for col in indicators]
    
    # Distribution des scores du pilier
    score_column = f"Score {pillar}"
    st.subheader(f"Distribution des scores {pillar}")
    fig = px.histogram(filtered_df, x=score_column, nbins=20,
                      color_discrete_sequence=["#2ca02c" if pillar == "Environnement" else 
                                              "#d62728" if pillar == "Social" else "#9467bd"])
    fig.update_layout(xaxis_title=f"Score {pillar}", yaxis_title="Nombre d'entreprises")
    st.plotly_chart(fig, use_container_width=True)
    
    # Scores moyens par indicateur (normalisé)
    st.subheader(f"Scores moyens par indicateur {pillar}")
    indicator_means = filtered_df[normalized_indicators].mean().reset_index()
    indicator_means.columns = ["Indicateur", "Score moyen"]
    indicator_means["Indicateur"] = indicator_means["Indicateur"].str.replace(" (normalisé)", "")
    
    fig = px.bar(indicator_means, x="Indicateur", y="Score moyen", 
                color="Score moyen", color_continuous_scale="viridis")
    fig.update_layout(xaxis_title="Indicateur", yaxis_title="Score moyen (normalisé)")
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Comparaison d'entreprises")
    
    # Sélection des entreprises à comparer
    companies = filtered_df["Entreprise"].unique().tolist()
    selected_companies = st.multiselect("Sélectionner des entreprises à comparer", companies, 
                                     default=companies[:3] if len(companies) >= 3 else companies)
    
    if selected_companies:
        comparison_df = filtered_df[filtered_df["Entreprise"].isin(selected_companies)]
        
        # Graphique radar pour comparer les entreprises sur les 3 piliers
        st.subheader("Comparaison des scores par pilier")
        
        fig = go.Figure()
        
        for company in selected_companies:
            company_data = comparison_df[comparison_df["Entreprise"] == company]
            fig.add_trace(go.Scatterpolar(
                r=[company_data["Score Environnement"].values[0], 
                   company_data["Score Social"].values[0], 
                   company_data["Score Gouvernance"].values[0],
                   company_data["Score Environnement"].values[0]],  # Pour fermer le polygone
                theta=["Environnement", "Social", "Gouvernance", "Environnement"],
                fill='toself',
                name=company
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Graphique en barres pour comparer les scores globaux
        st.subheader("Comparaison des scores CSR globaux")
        fig = px.bar(comparison_df, x="Entreprise", y="Score CSR Global", 
                    color="Entreprise", text="Score CSR Global")
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau de comparaison détaillé
        st.subheader("Tableau comparatif détaillé")
        comparison_cols = ["Entreprise", "Secteur", "Taille", "Pays", "Score Environnement", "Score Social", "Score Gouvernance", "Score CSR Global"]
        st.dataframe(comparison_df[comparison_cols], use_container_width=True)

with tab4:
    st.header("Comparaison par pays")
    
    # Nombre d'entreprises par pays
    st.subheader("Nombre d'entreprises par pays")
    country_counts = df["Pays"].value_counts().reset_index()
    country_counts.columns = ["Pays", "Nombre d'entreprises"]
    
    fig = px.bar(country_counts, x="Pays", y="Nombre d'entreprises", 
                color="Nombre d'entreprises", color_continuous_scale="blues")
    st.plotly_chart(fig, use_container_width=True)
    
    # Scores moyens par pays
    st.subheader("Scores CSR moyens par pays")
    country_scores = df.groupby("Pays")[["Score Environnement", "Score Social", "Score Gouvernance", "Score CSR Global"]].mean().reset_index()
    
    # Graphique radar pour comparer les pays
    selected_countries = st.multiselect(
        "Sélectionner des pays à comparer", 
        df["Pays"].unique().tolist(),
        default=df["Pays"].unique().tolist()[:5] if len(df["Pays"].unique()) >= 5 else df["Pays"].unique().tolist()
    )
    
    if selected_countries:
        filtered_country_scores = country_scores[country_scores["Pays"].isin(selected_countries)]
        
        # Graphique radar
        fig = go.Figure()
        
        for country in selected_countries:
            country_data = filtered_country_scores[filtered_country_scores["Pays"] == country]
            fig.add_trace(go.Scatterpolar(
                r=[country_data["Score Environnement"].values[0], 
                   country_data["Score Social"].values[0], 
                   country_data["Score Gouvernance"].values[0],
                   country_data["Score Environnement"].values[0]],  # Pour fermer le polygone
                theta=["Environnement", "Social", "Gouvernance", "Environnement"],
                fill='toself',
                name=country
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Graphique en barres pour les scores globaux par pays
        st.subheader("Scores CSR globaux par pays")
        fig = px.bar(filtered_country_scores.sort_values("Score CSR Global", ascending=False), 
                    x="Pays", y="Score CSR Global", 
                    color="Score CSR Global", color_continuous_scale="viridis",
                    text="Score CSR Global")
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau comparatif détaillé
        st.subheader("Tableau comparatif détaillé par pays")
        st.dataframe(filtered_country_scores, use_container_width=True)
    
    # Carte choroplèthe des scores par pays
    st.subheader("Répartition géographique des scores CSR")
    
    # Liste des codes ISO des pays pour la carte
    country_codes = {
        "France": "FRA", "Allemagne": "DEU", "Italie": "ITA", 
        "Espagne": "ESP", "Royaume-Uni": "GBR", "Belgique": "BEL", 
        "Pays-Bas": "NLD", "Suisse": "CHE", "Portugal": "PRT", "Suède": "SWE"
    }
    
    # Ajout des codes ISO
    country_scores["ISO"] = country_scores["Pays"].map(country_codes)
    
    # Création de la carte
    fig = px.choropleth(country_scores, 
                       locations="ISO",
                       color="Score CSR Global",
                       hover_name="Pays",
                       color_continuous_scale="viridis",
                       scope="europe",
                       labels={"Score CSR Global": "Score CSR"}
                      )
    
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyse spécifique par indicateur et par pays
    st.subheader("Analyse d'un indicateur spécifique par pays")
    
    # Sélection de l'indicateur à analyser
    all_indicators = []
    all_indicators.extend([f"{ind} (normalisé)" for ind in ["Émissions GES (tonnes CO2e)", 
                                                          "Consommation d'énergie renouvelable (%)",
                                                          "Déchets produits (tonnes)",
                                                          "Déchets recyclés (%)",
                                                          "Consommation d'eau (m³)",
                                                          "Production locale (%)"]])
    all_indicators.extend([f"{ind} (normalisé)" for ind in ["Part de femmes (%)", 
                                                          "Satisfaction employés (%)",
                                                          "Index Egapro (0-100)"]])
    all_indicators.extend([f"{ind} (normalisé)" for ind in ["Fournisseurs audités RSE (%)",
                                                          "Budget RSE (€)"]])
    
    selected_indicator = st.selectbox("Sélectionner un indicateur", all_indicators)
    
    # Calcul des moyennes par pays pour l'indicateur sélectionné
    indicator_by_country = df.groupby("Pays")[selected_indicator].mean().reset_index()
    indicator_by_country.columns = ["Pays", "Valeur moyenne"]
    
    # Graphique
    fig = px.bar(indicator_by_country.sort_values("Valeur moyenne", ascending=False), 
                x="Pays", y="Valeur moyenne", 
                color="Valeur moyenne", color_continuous_scale="viridis")
    st.plotly_chart(fig, use_container_width=True)

# Pied de page
st.markdown("---")
st.markdown("Dashboard développé pour le projet de plateforme de calcul de score CSR")


# In[ ]:




