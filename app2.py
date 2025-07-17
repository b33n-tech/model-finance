import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Données initiales ---
data = {
    'Poste': ['Loyer', 'Alimentation', 'Transport', 'Divertissement', 'Épargne', 'Assurances', 'Santé', 'Autres'],
    'Montant': [800, 300, 150, 100, 200, 100, 80, 70],
    'Classification': ['Indispensable', 'Indispensable', 'Indispensable', 'Superflu', 'Piliers', 'Indispensable', 'Indispensable', 'Superflu']
}

df = pd.DataFrame(data)

# --- Fonction de scoring ---
def score_financier(df):
    pond = {'Indispensable': 1.0, 'Piliers': 0.8, 'Superflu': 0.3}
    df['Poids'] = df['Classification'].map(pond)
    df['Score_poste'] = df['Montant'] * df['Poids']
    score = df['Score_poste'].sum()
    return score

# --- Calculs statistiques ---
def calc_stats(df):
    total = df['Montant'].sum()
    by_class = df.groupby('Classification')['Montant'].sum()
    score = score_financier(df)
    return total, by_class, score

# --- Sidebar inputs ---
st.sidebar.title("Modification des montants")

new_montants = []
for idx, row in df.iterrows():
    val = st.sidebar.number_input(
        f"{row['Poste']} ({row['Classification']})",
        min_value=0,
        value=row['Montant'],
        step=10,
        key=f"input_{idx}"
    )
    new_montants.append(val)

edited_df = df.copy()
edited_df['Montant'] = new_montants

# --- Calcul avant/après ---
total_before, by_class_before, score_before = calc_stats(df)
total_after, by_class_after, score_after = calc_stats(edited_df)

# --- Corps principal ---
st.title("Simulation multi-postes - Analyse stratégique budget")

# Comparaison tableau
st.subheader("Comparaison avant / après")
comp = pd.DataFrame({
    'Poste': df['Poste'],
    'Montant Avant (€)': df['Montant'],
    'Montant Après (€)': edited_df['Montant'],
    'Différence (€)': edited_df['Montant'] - df['Montant']
})
st.dataframe(comp.style.applymap(
    lambda v: 'color: red;' if v < 0 else ('color: green;' if v > 0 else ''),
    subset=['Différence (€)']
))

st.markdown(f"**Budget total avant :** {total_before:.2f} €  \n**Budget total après :** {total_after:.2f} €")
st.markdown(f"**Score financier avant :** {score_before:.2f}  \n**Score financier après :** {score_after:.2f}")

# Recommandations
def recommandations(comp, score_before, score_after, by_class_before, by_class_after):
    messages = []
    delta_score = score_after - score_before
    pct_delta_score = delta_score / score_before if score_before != 0 else 0

    if pct_delta_score < -0.1:
        messages.append("⚠️ Attention : votre score financier global diminue de plus de 10%. Faites attention à ne pas trop réduire les postes indispensables.")
    elif pct_delta_score > 0.05:
        messages.append("✅ Bonne nouvelle : votre score financier global augmente, ce qui indique une meilleure allocation selon le modèle.")

    for idx, row in comp.iterrows():
        if abs(row['Différence (€)']) > 1:
            cl = df.loc[df['Poste'] == row['Poste'], 'Classification'].values[0]
            diff = row['Différence (€)']
            if cl == 'Indispensable' and diff < 0:
                messages.append(f"⚠️ Réduction du poste indispensable '{row['Poste']}' de {abs(diff):.2f}€. Cela peut impacter négativement vos besoins essentiels.")
            elif cl == 'Superflu' and diff < 0:
                messages.append(f"👍 Réduction du poste superflu '{row['Poste']}' de {abs(diff):.2f}€ est une bonne optimisation.")
            elif cl == 'Piliers' and diff < 0:
                messages.append(f"⚠️ Réduction du poste pilier '{row['Poste']}' de {abs(diff):.2f}€. Réfléchissez bien à cet arbitrage.")

    for cl in ['Indispensable', 'Piliers', 'Superflu']:
        before = by_class_before.get(cl, 0)
        after = by_class_after.get(cl, 0)
        if before > 0:
            pct_change = (after - before) / before
            if cl == 'Indispensable' and pct_change < -0.1:
                messages.append(f"⚠️ Diminution > 10% des dépenses indispensables : {pct_change*100:.1f}%. Attention aux risques.")
            if cl == 'Superflu' and pct_change < -0.1:
                messages.append(f"✅ Diminution > 10% des dépenses superflues : {pct_change*100:.1f}%. Bon travail d’optimisation.")

    return messages

msgs = recommandations(comp, score_before, score_after, by_class_before, by_class_after)
if msgs:
    st.subheader("Recommandations stratégiques")
    for m in msgs:
        st.write(m)

# Visualisations
st.subheader("Visualisations")

fig, ax = plt.subplots(1, 2, figsize=(12, 5))
width = 0.35
x = np.arange(len(df))

ax[0].bar(x - width/2, df['Montant'], width, label='Avant')
ax[0].bar(x + width/2, edited_df['Montant'], width, label='Après')
ax[0].set_xticks(x)
ax[0].set_xticklabels(df['Poste'], rotation=45, ha='right')
ax[0].set_ylabel('Montant (€)')
ax[0].set_title('Dépenses par poste')
ax[0].legend()

cls_order = ['Indispensable', 'Piliers', 'Superflu']
before_vals = [by_class_before.get(cl, 0) for cl in cls_order]
after_vals = [by_class_after.get(cl, 0) for cl in cls_order]
x2 = np.arange(len(cls_order))

ax[1].bar(x2 - width/2, before_vals, width, label='Avant')
ax[1].bar(x2 + width/2, after_vals, width, label='Après')
ax[1].set_xticks(x2)
ax[1].set_xticklabels(cls_order)
ax[1].set_ylabel('Montant (€)')
ax[1].set_title('Répartition par classification')
ax[1].legend()

plt.tight_layout()
st.pyplot(fig)

# Objectif budget
st.subheader("Simulation d’objectif budgétaire")

objectif = st.number_input(
    "Fixer un objectif de budget total (laisser à 0 pour désactiver)",
    min_value=0,
    value=0,
    step=10
)

if objectif > 0:
    ecart = total_after - objectif
    st.write(f"Écart entre budget simulé et objectif : {ecart:.2f} €")
    if ecart > 0:
        st.write("💡 Vous dépassez votre objectif. Vous pouvez réduire les postes superflus ou piliers.")
    else:
        st.write("👍 Vous êtes sous votre objectif de budget.")
