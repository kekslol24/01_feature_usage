import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path
from datetime import  datetime

###### Set path for src import
projekt_root = Path(__file__).resolve().parents[2]
sys.path.append(str(projekt_root))

from src.lib import helpers

LOGO = "logo/klapp_logo.png"

###### Read in parquet 
df = pd.read_parquet("../../data/snapshot.parquet")

df["created_at"] = df["created_at"].dt.date
df["kuendigungsstatus"] = df["kuendigungsstatus"].dt.date
df["loeschstatus"] = df["loeschstatus"].dt.date
df = df.dropna(axis=0, how="all")

non_relevant_cols = ["name", "joker_tage_aktiviert", "loeschstatus", "kuendigungsstatus", "status"]
relevant_cols = df.columns.difference(non_relevant_cols)

mask = (
    df["name"].isna() & 
    (df["status"] == "Deaktiviert") #&
    # ((df[relevant_cols] == 0).all(axis=1))
)

df = df[~mask]

###### Title page
st.title("Feature-Usage Analyse")

st.logo(LOGO, size="large")

###### Initialize tabs

tab1, tab2 = st.tabs(["Feature-Analyse", "Gesamtübersicht"])


with tab1:

    ###### selectbox init
    selectbox = st.selectbox("Zeitraum:", ["Letzte 30 Tage", "Letzte 90 Tage", "Letztes Schuljahr", "Gesamter Zeitraum"])


    ###### selectbox mapping timeframes

    timeframes = {
        "Letzte 30 Tage": "_30_tage",
        "Letzte 90 Tage": "_90_tage",
        "Letztes Schuljahr": "_letztes_schuljahr",
        "Gesamter Zeitraum": "_historie"
    }

    searched_suffix = timeframes[selectbox]
    suitable_cols = df.columns[df.columns.str.contains(searched_suffix)]
    searchbox_cols = df[suitable_cols]

    st.write(selectbox)

    ###### Remove non int cols + Get total sum for overview 
    rest_cols = searchbox_cols.columns.difference(helpers.exception_cols)
    sum_digit_cols = searchbox_cols[rest_cols].sum().to_frame()

    ##### Reset index to avoid double index col for summmed feature chart, remove non important cols
    removed_cols = ["anzahl_aktive_schüler", "anzahl_aktive_lehrer"]
    keep_cols = sum_digit_cols.columns.difference(removed_cols)
    filtered_df = sum_digit_cols[keep_cols]
    
    bar_df_filtered = filtered_df.reset_index()
    bar_df_filtered = bar_df_filtered.rename(
        columns={"index": "feature", 0: "anzahl"}).sort_values("anzahl", ascending=False)

    fig = px.bar(bar_df_filtered, x="feature", y="anzahl", log_y=True)
    st.plotly_chart(fig)
    st.write(bar_df_filtered)

with tab2:
# ##### Creat searchbar for school name and plot overview table
    # Set table layout = wide
    st.set_page_config(layout="wide")

    historie_col = df.columns[df.columns.str.contains("_historie")]
    merged_col = pd.Index.union(historie_col, non_relevant_cols)
    overview_col = merged_col.union(removed_cols)

    txt_input = st.text_input(label="Suchfeld")
    filtered = df[df["name"].str.contains(txt_input)]
    

    st.dataframe(filtered, hide_index=True)

    ######## next -> create only historie view for overview