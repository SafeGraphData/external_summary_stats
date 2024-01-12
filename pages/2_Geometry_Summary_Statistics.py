import streamlit as st
from read_data import read_from_gsheets
import altair as alt
from datetime import datetime, timedelta
import pandas as pd
import streamlit.components.v1 as components
import plotly.express as px

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
            "Polygon coverage": lambda df: ((df["Polygon coverage"].str.replace(",", "").astype(float)) * 100).astype(float)
        }
    )
    .reset_index(drop=True)
)

latest_release_df_styled = (
    latest_release_df.style
    .apply(lambda x: ['background-color: #D7E8ED' if i%2==0 else '' for i in range(len(x))], axis=0)
    .format({
        "Total POI with Parking Lots": "{:,.0f}",
        "POI with polygons": "{:,.0f}",
        "Point-only POI": "{:,.0f}",
        "Polygon coverage": "{:.01f}%"
    })
)

total_poi = latest_release_df.iloc[-1]["Total POI with Parking Lots"]


st.write(f"POI count across all countries, including parking lots POI is <b>{total_poi:,.0f}</b>", unsafe_allow_html=True)
st.dataframe(latest_release_df_styled, use_container_width=True)

#### Top 30 Geometry ####
top_30_geometry_df = (
    read_from_gsheets("Countries")
    .assign(**{
        "Total POI with Parking Lots": lambda df: df["Total POI with Parking Lots"].astype(int),
        "POI with polygons": lambda df: df["POI with polygons"].str.replace(",", "").astype(int),
        "Point-only POI": lambda df: df["Point-only POI"].str.replace(",", "").astype(int),
        "Polygon coverage": lambda df: ((df["Polygon coverage"].str.replace(",", "").astype(float)) * 100).astype(float)
    })
    .query('iso_country_code != "US"')
    .rename(columns={"iso_country_code": "Country Code", "country": "Country"})
    [["Country Code", "Country", "Total POI with Parking Lots", "POI with polygons", "Point-only POI", "Polygon coverage"]]
    .head(30)
)

top_30_df_geometry_styled = (
    top_30_geometry_df.style
    .apply(lambda x: ['background-color: #D7E8ED' if i%2==0 else '' for i in range(len(x))], axis=0)
    .format({
       "Total POI with Parking Lots": "{:,.0f}",
        "POI with polygons": "{:,.0f}",
        "Point-only POI": "{:,.0f}",
        "Polygon coverage": "{:.01f}%"
    })
)

st.write("POI Counts - Top 30 Countries Outside the US")
st.dataframe(top_30_df_geometry_styled, use_container_width=True)


#### Last 12 Months Geometry ####

global_places_df = read_from_gsheets("Global Places")
global_places_df = global_places_df[["Release month", "Country", "POI with polygons"]]

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
last_12_months_df['POI with polygons'] = pd.to_numeric(last_12_months_df['POI with polygons'])

# st.dataframe(last_12_months_df)

last_12_months_geometry = alt.Chart(last_12_months_df).mark_bar().encode(
    x='Release month',
    y='POI with polygons',
    color='Country',
    tooltip=[alt.Tooltip('Release month'),
             alt.Tooltip('Country'),
             alt.Tooltip('POI with polygons', format=',')]
).properties(
    width=900,
    height=500,
    title=alt.TitleParams(
        text='Total POI with Polygon Count - Last 12 months',
        fontSize=18
    )
).configure_axisY(
    labelAngle=20
).configure_axisX(
    title=None,
    labelAngle=45
)

st.altair_chart(last_12_months_geometry, use_container_width=True)

#### Geometry Category Stats ####


category_stats_df = read_from_gsheets("Category stats")\
    [["Country", "naics_2", "naics_code", "safegraph_category", "safegraph_subcategory", "industry_title", "total_poi_count", "poi_with_polygon_count", "Polygon coverage"]]\
    .astype({'total_poi_count': int,"poi_with_polygon_count":int, "Polygon coverage":float })

global_df = category_stats_df.groupby(['naics_2', 'industry_title'])\
    .agg(total_poi_count=('total_poi_count', 'sum'), poi_with_polygon_count=("poi_with_polygon_count", "sum"))\
    .sort_values('poi_with_polygon_count', ascending=False)\
    .reset_index()\
    .rename(columns={"naics_2": "2-digit NAICS", "industry_title": "Industry Title", "total_poi_count": "Total POI", "poi_with_polygon_count":"POI with polygon count"})
global_df['Overall Polygon Coverage'] = (global_df['POI with polygon count'] /global_df['Total POI']) * 100

global_df_styled = global_df.drop(["Total POI"], axis=1).style.apply(lambda x: ['background-color: #D7E8ED' if i % 2 == 0 else '' for i in range(len(x))], axis=0)\
    .format({"POI with polygon count": "{:,}",
              "Overall Polygon Coverage": "{:.01f}%"})

countries = ['US', 'UK', 'CA']
dfs = []

for country in countries:
    df = (
        category_stats_df[category_stats_df['Country'] == country]
        [["naics_code", "safegraph_category", "safegraph_subcategory", "poi_with_polygon_count", "Polygon coverage"]]
        .rename(columns={"naics_code": "NAICS Code", "safegraph_category": "SafeGraph Category",\
                         "safegraph_subcategory": "SafeGraph Subcategory", "poi_with_polygon_count": "POI with Polygon Count"})
        .assign(**{
            "Polygon coverage": lambda df: ((df["Polygon coverage"]) * 100).astype(float)
    }).sort_values('POI with Polygon Count', ascending=False)
        .reset_index(drop=True)
    )

    df['POI with Polygon Count'] = df['POI with Polygon Count'].astype(int).apply(lambda x: "{:,}".format(x))
    df['Polygon coverage'] = df['Polygon coverage'].astype(float).apply(lambda x: "{:.01f}%".format(x))
    dfs.append(df)

styled_dfs = [
    df.style.apply(lambda x: ['background-color: #D7E8ED' if i % 2 == 0 else '' for i in range(len(x))], axis=0)
    for df in dfs
]

tabs = st.tabs(["Global"] + countries)
with tabs[0]:
    # st.write("Global POI Count")
    st.dataframe(global_df_styled, use_container_width=True)

for i, tab in enumerate(tabs[1:]):
    with tab:
        if i < len(styled_dfs):
            # st.write(f"{countries[i]} POI Count")
            st.dataframe(styled_dfs[i], use_container_width=True)

####Parking coverage by region ####

state_df = read_from_gsheets("Parking - regions").assign(**{
        "total_parking_poi": lambda df: df["total_parking_poi"].astype(int),
        "%_poi_with_parking": lambda df: ((df["pct_poi_with_parking"].astype(float)) * 100).astype(float)
    }).rename(columns={"%_poi_with_parking": "% of POI with Parking Lot"})

state_df['% of POI with Parking Lot'] = [round(x,1) for x in state_df['% of POI with Parking Lot']]
state_df['total_parking_poi'] = state_df['total_parking_poi'].map('{:,.0f}'.format)

# Create the plot with USA scope, gray background, and tooltips
fig = px.choropleth(state_df,
                    locations='state',
                    color='% of POI with Parking Lot',
                    hover_name='state',
                    locationmode='USA-states',  # Use predefined US state boundaries
                    scope='usa',  # Set the scope to 'usa'
                    title='Parking Coverage by Region',
                     color_continuous_scale=px.colors.diverging.RdYlGn,  # Reverse Reds color scale
                    range_color=[40, 80],  # Specify the range for the color scale
                    )

# Customize the background color
fig.update_layout(
    geo=dict(
        bgcolor='lightgray',  # Set the background color
    )
)

# Add tooltips with state information
fig.update_traces(hovertemplate='State:  <b>%{hovertext}</b><br>% POI with Parking: %{z}%<br>Total Parking POI: %{text}<extra></extra>',
                  text=state_df['total_parking_poi'])

fig.update_layout(
    legend=dict(
        orientation='h',  # Set the orientation to horizontal
        x=0,  # Set the x position
        y=1.02,  # Set the y position
       # xanchor='left',  # Set the x anchor to left
        yanchor='bottom'  # Set the y anchor to bottom
    )
)
fig.update_layout(height=800, width=1400) 
st.write('See the map below, where states are shaded based on the percentage of POI that have an associated parking lot POI')
st.plotly_chart(fig)

#### Geometry Category Stats ####


category_stats_parking_df = read_from_gsheets('Parking - categories')\
    [["naics_code", "safegraph_category", "safegraph_subcategory", "total_open_poi_count", "total_parking_poi", "pct_poi_with_parking"]]\
    .astype({'naics_code': str})

category_stats_parking_df['total_open_poi_count'] =[int(x) for x in category_stats_parking_df['total_open_poi_count'] ]
category_stats_parking_df['total_parking_poi'] = [0 if (pd.isna(x)) or (x=="NaN")  else int(x) for x in category_stats_parking_df['total_parking_poi'] ]
category_stats_parking_df['pct_poi_with_parking'] = [0 if (pd.isna(x)) or (x=="NaN") else float(x) for x in category_stats_parking_df['pct_poi_with_parking'] ]
category_stats_parking_df['naics_code'] = [x.split(".")[0] for x in category_stats_parking_df['naics_code'] ]


df = (
    category_stats_parking_df
    .rename(columns={"naics_code": "NAICS Code", "safegraph_category": "SafeGraph Category",\
                        "safegraph_subcategory": "SafeGraph Subcategory", "total_open_poi_count": "Total Open POI Count",\
                           "pct_poi_with_parking":"Pct POI With Parking", "total_parking_poi":"Total Parking POI" })
    .assign(**{
        "Pct POI With Parking": lambda df: ((df["Pct POI With Parking"]) * 100).astype(float)
}).sort_values('Total Open POI Count', ascending=False)
    .reset_index(drop=True)
)

df['Total Open POI Count'] = df['Total Open POI Count'].astype(int).apply(lambda x: "{:,}".format(x))
df['Pct POI With Parking'] = df['Pct POI With Parking'].astype(float).apply(lambda x: "{:.01f}%".format(x))
df['Total Parking POI'] = df['Total Parking POI'].astype(int).apply(lambda x: "{:,}".format(x))

styled_df = (
    df.style.apply(lambda x: ['background-color: #D7E8ED' if i % 2 == 0 else '' for i in range(len(x))], axis=0)
)

st.write("Parking Coverage by Category")
st.dataframe(styled_df, use_container_width=True)


#### Geometry Brand Category Stats ####


brand_stats_parking_df = read_from_gsheets('Parking - brands')\
    [["primary_brand","naics_code", "safegraph_category", "safegraph_subcategory", "pct_poi_with_parking", 'total_open_poi_count']]\
    .astype({'naics_code': str, 'total_open_poi_count':int})


brand_stats_parking_df = brand_stats_parking_df[brand_stats_parking_df['total_open_poi_count']>=100].drop(['total_open_poi_count'], axis=1)


brand_stats_parking_df['pct_poi_with_parking'] = [0 if (pd.isna(x)) or (x=="NaN") else float(x) for x in brand_stats_parking_df['pct_poi_with_parking'] ]
brand_stats_parking_df['naics_code'] = [x.split(".")[0] for x in brand_stats_parking_df['naics_code'] ]


parking_brand_df = (
    brand_stats_parking_df
    .rename(columns={"naics_code": "NAICS Code", "safegraph_category": "SafeGraph Category",\
                        "safegraph_subcategory": "SafeGraph Subcategory",  "pct_poi_with_parking":"Pct POI With Parking",\
                              "primary_brand":"Brand Name" })
    .assign(**{
        "Pct POI With Parking": lambda df: ((df["Pct POI With Parking"]) * 100).astype(float)
}).sort_values('Pct POI With Parking', ascending=False)
    .reset_index(drop=True)
)


parking_brand_df['Pct POI With Parking'] = parking_brand_df['Pct POI With Parking'].astype(float).apply(lambda x: "{:.01f}%".format(x))


styled_brand_df = (
    parking_brand_df.style.apply(lambda x: ['background-color: #D7E8ED' if i % 2 == 0 else '' for i in range(len(x))], axis=0)
)

st.write("Parking Coverage by Brand")
st.dataframe(styled_brand_df, use_container_width=True)

