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

###### Read in parquet 
df = pd.read_parquet("../../data/snapshot.parquet")

df["created_at"] = df["created_at"].dt.date

# Set table layout = wide
st.set_page_config(layout="wide")

###### Remove non int cols + Get total sum for overview 
rest_cols = df.columns.difference(helpers.exception_cols)
sum_digit_cols = df[rest_cols].sum().to_frame()

##### for summmed feature chart, remove non important cols
removed_cols = ["anzahl_aktive_schüler", "anzahl_aktive_lehrer"]
keep_cols = sum_digit_cols.columns.difference(removed_cols)
filtered_df = sum_digit_cols[keep_cols]

##### Reset index to avoid double index col
bar_df_filtered = filtered_df.reset_index()
bar_df_filtered = bar_df_filtered.rename(columns={"index": "feature", 0: "anzahl"}).sort_values("anzahl", ascending=False)
st.write(bar_df_filtered)

fig = px.bar(bar_df_filtered, x="feature", y="anzahl", log_y=True)
st.plotly_chart(fig)
# ##### Creat searchbar for school name and plot overview table
# txt_input = st.text_input(label="Suchfeld")
# filtered = df[df["name"].str.contains(txt_input)]

# st.title("Feature-Usage Analyse")
# st.dataframe(df)