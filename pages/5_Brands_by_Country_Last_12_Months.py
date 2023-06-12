import streamlit as st
import pandas as pd
import altair as alt
from read_data import read_from_gsheets
from datetime import datetime, timedelta

global_places_df = read_from_gsheets("Global Places")
global_places_df = global_places_df[["Release month", "Country", "Distinct brands"]]

for i, value in enumerate(global_places_df['Release month']):
    try:
        global_places_df.loc[i, 'Release month'] = pd.to_datetime(value, format='%b %Y').strftime('%Y-%m')
    except ValueError:
        global_places_df.loc[i, 'Release month'] = pd.to_datetime(value, format='%B %Y').strftime('%Y-%m')

start_date_str = (datetime.now() - timedelta(days=365)).strftime("%Y-%m")

global_places_df["Release month"] = pd.to_datetime(global_places_df["Release month"])
brands_by_country_df = global_places_df[
    (global_places_df["Release month"] >= start_date_str) & (global_places_df["Release month"] <= datetime.now()) &
    (global_places_df["Country"] != "Grand Total")
]
brands_by_country_df["Release month"] = brands_by_country_df["Release month"].dt.strftime("%Y-%m")
brands_by_country_df["Distinct brands"] = pd.to_numeric(brands_by_country_df["Distinct brands"])

# st.dataframe(brands_by_country_df)

brands_by_country = alt.Chart(brands_by_country_df).mark_bar().encode(
    x='Release month',
    y='Distinct brands',
    color='Country',
    tooltip=[alt.Tooltip('Release month'),
             alt.Tooltip('Country'),
             alt.Tooltip('Distinct brands', format=',')]
).properties(
    width=900,
    height=500,
    title=alt.TitleParams(
        text='Distinct Brand Count by Country - Last 12 months',
        fontSize=18
    )
).configure_axisY(
    labelAngle=0
).configure_axisX(
    title=None,
    labelAngle=45
)

st.altair_chart(brands_by_country)