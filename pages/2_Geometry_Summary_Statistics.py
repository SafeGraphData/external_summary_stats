import streamlit as st
from read_data import read_from_gsheets
import altair as alt
from datetime import datetime, timedelta
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Geometry Summary Statistics",
    layout="wide"
)

latest_release_df = (
    read_from_gsheets("Global Places")
    [["Country", "Total POI with Parking Lots", "POI with polygons", "Point-only POI", "Polygon coverage"]]
    .tail(7)
    .assign(
        **{
            "Total POI with Parking Lots": lambda df: df["Total POI with Parking Lots"].str.replace(",", "").astype(float),
            "POI with polygons": lambda df: df["POI with polygons"].str.replace(",", "").astype(int),
            "Point-only POI": lambda df: df["Point-only POI"].str.replace(",", "").astype(int),
            "Polygon coverage": lambda df: (df["Polygon coverage"].str.replace(",", "").astype(float)) * 100
        }
    )
    .reset_index(drop=True)
)

latest_release_df_styled = (
    latest_release_df.style
    .apply(lambda x: ['background-color: #D7E8ED' if i%2==0 else '' for i in range(len(x))], axis=0)
    .format({
        "Total POI with Parking Lots": "{:,.0f}",
        "Polygon coverage": "{:.1f}%"
    })
)

total_poi = latest_release_df.iloc[-1]["Total POI with Parking Lots"]


st.write(f"POI count across all countries, including parking lots POI is <b>{total_poi:,.0f}</b>", unsafe_allow_html=True)
st.dataframe(latest_release_df_styled, use_container_width=True)
