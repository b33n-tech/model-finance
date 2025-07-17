import streamlit as st
import pandas as pd

st.set_page_config(page_title="Modèle financier avec timeline", layout="wide")
st.title("Modèle financier personnel stratégique avec timeline")

# --- Paramètres durée simulation ---
mois_max = st.sidebar.slider("Durée de la simulation (mois)", 6, 24, 12)

# --- Budget de base mensuel ---
postes = ['Loyer', 'Alimentation', 'Transport', 'Divertissement', 'Épargne', 'Assurances', 'Santé', 'Autres']
st.sidebar.header("Budget mensuel de base par poste")
base_montants = {}
for poste in postes:
    base_montants[poste] = st.sidebar.number_input(poste, min_value=0, value=100, step=10)

# --- Gestion événements financiers ponctuels ---
if 'events' not in st.session_state:
    st.session_state['events'] = pd.DataFrame(columns=['Mois', 'Type', 'Poste', 'Montant', 'Description'])

st.subheader("Ajouter un événement financier ponctuel")

with st.form("ajout_event"):
    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        mois = st.number_input("Mois (1 à {})".format(mois_max), min_value=1, max_value=mois_max, value=1)
        type_event = st.selectbox("Type", ['Dépense', 'Revenu', 'Investissement'])
    with col2:
        poste = st.selectbox("Poste", postes)
        montant = st.number_input("Montant (€)", value=0.0, step=10.0)
    with col3:
        desc = st.text_input("Description")
    
    submitted = st.form_submit_button("Ajouter")
    if submitted:
        new_event = {'Mois': mois, 'Type': type_event, 'Poste': poste, 'Montant': montant, 'Description': desc}
        st.session_state['events'] = pd.concat([st.session_state['events'], pd.DataFrame([new_event])], ignore_index=True)
        st.success(f"Événement ajouté : {type_event} de {montant} € sur {poste} au mois {mois}")

st.markdown("---")

# --- Afficher les événements ---
st.subheader("Événements financiers enregistrés")
st.dataframe(st.session_state['events'])

# --- Préparer la simulation timeline ---
timeline = pd.DataFrame(0.0, index=range(1, mois_max+1), columns=postes)

# Remplir budget mensuel de base
for poste, val in base_montants.items():
    timeline[poste] = val

# Appliquer événements
for _, event in st.session_state['events'].iterrows():
    mois = int(event['Mois'])
    if 1 <= mois <= mois_max:
        poste = event['Poste']
        montant = float(event['Montant'])
        # Ajuster signe selon type
        if event['Type'] == 'Dépense':
            timeline.at[mois, poste] -= montant
        else:
            timeline.at[mois, poste] += montant

# Calculs totaux
timeline['Total mensuel'] = timeline.sum(axis=1)
timeline['Total cumulé'] = timeline['Total mensuel'].cumsum()

# --- Affichage visualisations ---
st.subheader(f"Simulation financière sur {mois_max} mois")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Budget mensuel par poste (mois par mois)")
    st.line_chart(timeline[postes])

with col2:
    st.markdown("### Totaux mensuels et cumulés")
    st.line_chart(timeline[['Total mensuel', 'Total cumulé']])

st.markdown("---")
st.write("Tu peux modifier les montants de base et ajouter/supprimer des événements pour tester différents scénarios et voir l’impact sur ta gestion financière dans le temps.")

