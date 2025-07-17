import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans

st.set_page_config(page_title="🧠 Analyse de ton budget personnel", layout="wide")
st.title("💸 Analyse stratégique de ton budget personnel")

uploaded_file = st.file_uploader("📂 Uploade ton budget (Excel ou CSV)", type=["xlsx", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("🔍 Ton budget importé")
    st.dataframe(df)

    required_cols = ["Catégorie", "Description", "Montant", "Pertinence (1-5)"]
    if all(col in df.columns for col in required_cols):
        # Clustering des dépenses
        X = df[["Montant", "Pertinence (1-5)"]]
        kmeans = KMeans(n_clusters=3, random_state=0)
        df["Cluster"] = kmeans.fit_predict(X)

        # Attribution manuelle des clusters
        # On trie les clusters selon pertinence + montant
        cluster_means = df.groupby("Cluster")[["Montant", "Pertinence (1-5)"]].mean()
        mapping = {
            cluster_means.sort_values(["Montant", "Pertinence (1-5)"], ascending=False).index[0]: "🧱 Pilier de vie",
            cluster_means.sort_values(["Montant", "Pertinence (1-5)"], ascending=True).index[0]: "🧹 Gaspillage potentiel",
            cluster_means.index.difference([
                cluster_means.sort_values(["Montant", "Pertinence (1-5)"], ascending=False).index[0],
                cluster_means.sort_values(["Montant", "Pertinence (1-5)"], ascending=True).index[0]
            ])[0]: "🌀 Zone grise / arbitrable"
        }
        df["Type de dépense"] = df["Cluster"].map(mapping)

        st.subheader("📊 Résultat de l’analyse")
        st.dataframe(df[["Catégorie", "Description", "Montant", "Pertinence (1-5)", "Type de dépense"]])

        st.subheader("📈 Carte stratégique des dépenses")
        fig = px.scatter(df, 
                         x="Pertinence (1-5)", 
                         y="Montant", 
                         size="Montant",
                         color="Type de dépense",
                         hover_data=["Catégorie", "Description"],
                         title="Montant vs Pertinence")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📍 Répartition globale")
        st.plotly_chart(px.pie(df, names="Type de dépense", values="Montant"), use_container_width=True)

        st.subheader("📌 Dépenses par catégorie")
        bar = px.bar(df, x="Catégorie", y="Montant", color="Type de dépense", barmode="group")
        st.plotly_chart(bar, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("💾 Télécharger les résultats", csv, "budget_analysé.csv", "text/csv")

    else:
        st.error("Ton fichier doit avoir les colonnes : 'Catégorie', 'Description', 'Montant', 'Pertinence (1-5)'")

else:
    st.info("Tu peux aussi saisir ton budget dans Excel et l’uploader ici.")
