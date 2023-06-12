import streamlit as st
import pandas as pd
import altair as alt
from read_data import read_from_gsheets
from datetime import datetime, timedelta

global_places_df = read_from_gsheets("Global Places")
global_places_df = global_places_df[["Release month", "Country", "Total POI"]]

for i, value in enumerate(global_places_df['Release month']):
    try:
        global_places_df.loc[i, 'Release month'] = pd.to_datetime(value, format='%b %Y').strftime('%Y-%m')
    except ValueError:
        global_places_df.loc[i, 'Release month'] = pd.to_datetime(value, format='%B %Y').strftime('%Y-%m')

start_date_str = (datetime.now() - timedelta(days=365)).strftime("%Y-%m")

global_places_df["Release month"] = pd.to_datetime(global_places_df["Release month"])
last_12_months_df = global_places_df[
    (global_places_df["Release month"] >= start_date_str) & (global_places_df["Release month"] <= datetime.now()) &
    (global_places_df["Country"] != "Grand Total")
]
last_12_months_df["Release month"] = last_12_months_df["Release month"].dt.strftime("%Y-%m")
last_12_months_df['Total POI'] = pd.to_numeric(last_12_months_df['Total POI'])

# st.dataframe(last_12_months_df)

last_12_months = alt.Chart(last_12_months_df).mark_bar().encode(
    x='Release month',
    y='Total POI',
    color='Country',
    tooltip=[alt.Tooltip('Release month'),
             alt.Tooltip('Country'),
             alt.Tooltip('Total POI', format=',')]
).properties(
    width=900,
    height=500,
    title=alt.TitleParams(
        text='Total POI Count - Last 12 months',
        fontSize=18
    )
).configure_axisY(
    labelAngle=20
).configure_axisX(
    title=None,
    labelAngle=45
)

st.altair_chart(last_12_months)

