import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

projekt_root = Path(__file__).resolve().parents[2]
sys.path.append(str(projekt_root))

from src.lib import helpers

df = pd.read_parquet("../../data/snapshot.parquet")

st.set_page_config(layout="wide")

rest_cols = df.columns.difference(helpers.exception_cols)
sum_digit_cols = df[rest_cols].sum().to_frame()

st.write(sum_digit_cols.T)
fig = px.imshow(sum_digit_cols.T)
st.plotly_chart(fig)

txt_input = st.text_input(label="Suchfeld")
filtered = df[df["name"].str.contains(txt_input)]

st.title("Feature-Usage Analyse")
st.dataframe(df)