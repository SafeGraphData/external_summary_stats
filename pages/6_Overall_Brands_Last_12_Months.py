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
overall_brands_last_12_df = global_places_df[
    (global_places_df["Release month"] >= start_date_str) & (global_places_df["Release month"] <= datetime.now()) &
    (global_places_df["Country"] == "Grand Total")
]
overall_brands_last_12_df["Release month"] = overall_brands_last_12_df["Release month"].dt.strftime("%Y-%m")
overall_brands_last_12_df["Distinct brands"] = pd.to_numeric(overall_brands_last_12_df["Distinct brands"])
overall_brands_last_12_df = overall_brands_last_12_df.rename(columns={"Distinct brands": "Distinct brands - overall"})

# st.dataframe(overall_brands_last_12_df)

y_min = overall_brands_last_12_df['Distinct brands - overall'].min()
y_max = overall_brands_last_12_df['Distinct brands - overall'].max()
y_range = [y_min, y_max]

overall_brands_last_12 = alt.Chart(overall_brands_last_12_df).mark_line().encode(
    x='Release month',
    y=alt.Y('Distinct brands - overall', scale=alt.Scale(domain=y_range)),
    tooltip=[alt.Tooltip('Release month'),
             alt.Tooltip('Country'),
             alt.Tooltip('Distinct brands - overall', format=',')]
).properties(
    width=800,
    height=400,
    title=alt.TitleParams(
        text='Distinct Brand Count Overall - Last 12 months',
        fontSize=18
    )
).configure_axisX(
    title=None,
    labelAngle=45
)

st.altair_chart(overall_brands_last_12)