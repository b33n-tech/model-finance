import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Recherche optimale de modèle financier", layout="wide")
st.title("Optimisation de la gestion budgétaire par simulation multi-scénarios")

# --- Paramètres de simulation ---
mois_max = st.sidebar.slider("Durée simulation (mois)", 6, 24, 12)
nb_scenarios = st.sidebar.slider("Nombre de scénarios à générer", 10, 200, 100)

postes = ['Loyer', 'Alimentation', 'Transport', 'Divertissement', 'Épargne', 'Assurances', 'Santé', 'Autres']

st.sidebar.header("Budget mensuel de base par poste")
base_montants = {}
for poste in postes:
    base_montants[poste] = st.sidebar.number_input(poste, min_value=0, value=100, step=10)

st.sidebar.header("Plages de variation en % autour du budget de base")
variations = {}
for poste in postes:
    pct = st.sidebar.slider(f"Variation % {poste}", 0, 50, 20)
    variations[poste] = pct / 100  # ex: 0.2 = ±20%

# Critères filtrage
max_depense_moyenne = st.sidebar.number_input("Dépense max moyenne par mois (€)", min_value=0, value=2500, step=100)

# Fonction pour générer un scénario selon variations autour du base
def generer_scenario(base, var_pct, mois):
    """
    Génère un dataframe [mois x postes] avec montants variables dans plages ±var_pct
    """
    df = pd.DataFrame(index=range(1, mois+1), columns=base.keys())
    for poste, val in base.items():
        low = val * (1 - var_pct[poste])
        high = val * (1 + var_pct[poste])
        # Pour chaque mois, tirage uniforme dans [low, high]
        df[poste] = np.random.uniform(low, high, size=mois)
    return df

# Générer tous les scénarios
scenarios = []
for i in range(nb_scenarios):
    df_s = generer_scenario(base_montants, variations, mois_max)
    # Assurer que l'épargne n'est pas négative
    df_s['Épargne'] = df_s['Épargne'].clip(lower=0)

    # Calcul dépenses totales = somme postes sauf épargne
    df_s['Dépenses totales'] = df_s.drop(columns=['Épargne']).sum(axis=1)
    # Total mensuel = dépenses + épargne
    df_s['Total mensuel'] = df_s[postes].sum(axis=1)
    # Épargne cumulée dans le temps
    df_s['Épargne cumulée'] = df_s['Épargne'].cumsum()

    # Calcul métriques clés
    dep_moy = df_s['Dépenses totales'].mean()
    epargne_finale = df_s['Épargne cumulée'].iloc[-1]
    epargne_rapide = df_s['Épargne cumulée'].iloc[mois_max//3] if mois_max>=3 else epargne_finale

    scenarios.append({
        'index': i,
        'df': df_s,
        'depense_moyenne': dep_moy,
        'epargne_finale': epargne_finale,
        'epargne_rapide': epargne_rapide
    })

# Filtrer scénarios selon critère dépenses max
scenarios_filtres = [sc for sc in scenarios if sc['depense_moyenne'] <= max_depense_moyenne]

# Trier par épargne finale décroissante
top_par_final = sorted(scenarios_filtres, key=lambda x: x['epargne_finale'], reverse=True)[:3]

# Trier par épargne rapide décroissante
top_par_rapide = sorted(scenarios_filtres, key=lambda x: x['epargne_rapide'], reverse=True)[:3]

# Affichage résultats
st.subheader("Top 3 scénarios par épargne finale maximale")
for i, scen in enumerate(top_par_final, 1):
    st.markdown(f"### Scénario #{scen['index']}")
    st.write(f"Dépense moyenne mensuelle : {scen['depense_moyenne']:.2f} €")
    st.write(f"Épargne finale : {scen['epargne_finale']:.2f} €")
    st.line_chart(scen['df'][postes + ['Dépenses totales', 'Épargne cumulée']])
    st.dataframe(scen['df'][postes].mean().to_frame(name='Montant moyen (€)').sort_values(by='Montant moyen (€)', ascending=False))

st.markdown("---")

st.subheader("Top 3 scénarios par épargne rapide (1/3 de la période)")
for i, scen in enumerate(top_par_rapide, 1):
    st.markdown(f"### Scénario #{scen['index']}")
    st.write(f"Dépense moyenne mensuelle : {scen['depense_moyenne']:.2f} €")
    st.write(f"Épargne après 1/3 période : {scen['epargne_rapide']:.2f} €")
    st.line_chart(scen['df'][postes + ['Dépenses totales', 'Épargne cumulée']])
    st.dataframe(scen['df'][postes].mean().to_frame(name='Montant moyen (€)').sort_values(by='Montant moyen (€)', ascending=False))

st.markdown("""
---
💡 **Explications** :  
- Chaque scénario teste une combinaison de budgets mensuels variables dans les plages définies (%).  
- On calcule plusieurs métriques pour juger de la qualité du modèle financier : épargne totale finale, vitesse d’épargne, dépenses moyennes.  
- Tu peux ajuster la durée, le nombre de scénarios, la base budgétaire et les plages de variations pour explorer différents profils.  
""")
