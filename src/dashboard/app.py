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

tab1, tab2, tab3 = st.tabs(["Gesamtübersicht", "Feature-Analyse", "Schule im Detail"], key="active_tab")

###### column handling

historie_col = df.columns[df.columns.str.contains("_historie")]
removed_cols = ["anzahl_aktive_schüler", "anzahl_aktive_lehrer"]
spalten_reihenfolge = [
    "name", 
    "created_at", 
    "status", 
    "kuendigungsstatus", 
    "loeschstatus", 
    "joker_tage_aktiviert"] + list(removed_cols) + list(historie_col) 

non_relevant_cols = ["name", "joker_tage_aktiviert", "loeschstatus", "kuendigungsstatus", "status", "created_at"]
relevant_cols = df.columns.difference(non_relevant_cols)

with tab1:
# ##### Creat searchbar for school name and plot overview table
    # Set table layout = wide
    st.set_page_config(layout="wide")

    #### set session_state for click to tab 3 redirect
    
    merged_col = pd.Index.union(historie_col, non_relevant_cols)
    overview_col = merged_col.union(removed_cols)

    txt_input = st.text_input(label="Suchfeld",  key="Gesamtübersicht")
    filtered = df[df["name"].str.contains(txt_input, case=False)]
    df_cols = filtered[spalten_reihenfolge]
    
    # st.multiselect()

    #### logic to set session_state to selected name in overview, of not selected return none so it resets
    event = st.dataframe(df_cols, on_select="rerun", selection_mode="single-row", hide_index=True)
    if event["selection"]["rows"]:
        zeilen_index = event["selection"]["rows"][0]
        selected_name = df_cols.iloc[zeilen_index]["name"]
        st.session_state["selected_name"] = selected_name
    else:
        st.session_state["selected_name"] = None

with tab2:

    ###### selectbox init
    selectbox = st.selectbox("Zeitraum:", 
                             ["Letzte 30 Tage", 
                              "Letzte 90 Tage", 
                              "Letztes Schuljahr", "Gesamter Zeitraum"
                              ], key="Feature Analyse")


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

    ###### Remove non int cols + Get total sum for overview 
    rest_cols = searchbox_cols.columns.difference(helpers.exception_cols)
    sum_digit_cols = searchbox_cols[rest_cols].sum().to_frame()

    ##### Reset index to avoid double index col for summmed feature chart, remove non important cols

    keep_cols = sum_digit_cols.columns.difference(removed_cols)
    filtered_df = sum_digit_cols[keep_cols]
    
    bar_df_filtered = filtered_df.reset_index()
    bar_df_filtered = bar_df_filtered.rename(
        columns={"index": "feature", 0: "anzahl"}).sort_values("anzahl", ascending=False)

    fig = px.bar(bar_df_filtered, x="feature", y="anzahl", log_y=True)
    st.plotly_chart(fig)
    st.write(bar_df_filtered)

with tab3:
    ##### Initialize columns for widgets
    col1, col2, col3, col4 ,col5 = st.columns(5)

    options = [""] + list(df_cols["name"].unique())
    selected_school = st.selectbox("Schule suchen", options, key="Schule im Detail")

    if st.session_state.get("selected_name") is not None:
        name = df[df["name"] == st.session_state.get("selected_name")]
        st.header(name.iloc[0]["name"])
    else:
        name = df_cols[df_cols["name"] == selected_school]
        st.header(name.iloc[0]["name"])



    if name.iloc[0]["status"] == "Aktiv":
        st.success("Aktiv")
    else:
        st.error("Nicht Aktiv")


    with col1:
        st.metric("Aktive Lehrer", name.iloc[0]["anzahl_aktive_lehrer"])

    with col2:
        st.metric("Aktive Schüler", name.iloc[0]["anzahl_aktive_schüler"])

    with col3:
        if pd.isna(name.iloc[0]["kuendigungsstatus"]):
            st.metric("Kündigungsstatus", "Nicht Gekündigt")
        else:
            datum = name.iloc[0]["kuendigungsstatus"]
            st.metric("Kündigungsdatum", datum.strftime("%d.%m.%Y"))

    # with col4: 
    #     if pd.isna(name.iloc[0][""]):
    #         pass

    with col5:
        formatted_currency = f"CHF {name.iloc[0]["anzahl_invoices_historie"]:,.2f}".replace(",", "'")
        st.metric("Rechnungsbetrag (Historie)", formatted_currency)
    
    st.dataframe(name, hide_index=True)