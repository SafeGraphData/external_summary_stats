import streamlit as st
from read_data import read_from_gsheets
import altair as alt
from datetime import datetime, timedelta
import pandas as pd
import streamlit.components.v1 as components



st.set_page_config(
    page_title="Places Summary Statistics",
    layout="wide"
)
#### Latest Release ####
latest_release_df = (
    read_from_gsheets("Global Places")
    [["Country", "Total POI with Parking Lots", "Distinct brands", "Branded POI", "Total POI"]]
    .tail(7)
    .assign(
        **{
            "Total POI with Parking Lots": lambda df: df["Total POI with Parking Lots"].str.replace(",", "").astype(float),
            "Total POI": lambda df: df["Total POI"].str.replace(",", "").astype(int),
            "Branded POI": lambda df: df["Branded POI"].str.replace(",", "").astype(int),
            "% Branded": lambda df: (df["Branded POI"] / df["Total POI"]) * 100,
            "Distinct brands": lambda df: df["Distinct brands"].astype(int)
        }
    )
    .drop(["Branded POI", "Total POI"], axis=1)
    .reset_index(drop=True)
)

latest_release_df_styled = (
    latest_release_df.style
    .apply(lambda x: ['background-color: #D7E8ED' if i%2==0 else '' for i in range(len(x))], axis=0)
    .format({
        "Total POI with Parking Lots": "{:,.0f}",
        "% Branded": "{:.1f}%",
        "Distinct brands": "{:,.0f}"
    })
)

total_poi = latest_release_df.iloc[-1]["Total POI with Parking Lots"]

parking_lots_df = (
    read_from_gsheets("Parking")
    .assign(**{
        "Distinct brands": "NA",
        "% Branded": "NA",
        "Total POI": lambda df: df["Total POI"].str.replace(",", "").astype(int)
    })
    [["Country", "Total POI", "Distinct brands", "% Branded"]]
)

parking_lots_df_styled = (
    parking_lots_df.style
    .apply(lambda x: ['background-color: #D7E8ED' if i % 2 == 0 else '' for i in range(len(x))], axis=0)
    .format({
        "Total POI": "{:,.0f}"
    })
)

st.write(f"Total POI count across countries, including parking lots POI is <b>{total_poi:,.0f}</b>", unsafe_allow_html=True)
st.dataframe(latest_release_df_styled, use_container_width=True)
st.write("Latest Release - Parking")
st.dataframe(parking_lots_df_styled, use_container_width=True)

### Top 30 ###
top_30_df = (
    read_from_gsheets("Countries")
    .assign(**{
        "Distinct brands": lambda df: df["Distinct brands"].astype(int),
        "Total POI": lambda df: df["Total POI"].str.replace(",", "").astype(int),
        "Branded POI": lambda df: df["Branded POI"].str.replace(",", "").astype(int),
        "% Branded": lambda df: (df["Branded POI"] / df["Total POI"]) * 100
    })
    .query('iso_country_code != "US"')
    .rename(columns={"iso_country_code": "Country Code", "country": "Country"})
    [["Country Code", "Country", "Total POI", "Distinct brands", "% Branded"]]
    .head(30)
)

top_30_df_styled = (
    top_30_df.style
    .apply(lambda x: ['background-color: #D7E8ED' if i%2==0 else '' for i in range(len(x))], axis=0)
    .format({
        "Total POI": "{:,.0f}",
        "Distinct brands": "{:,.0f}",
        "Branded POI": "{:,.0f}",
        "% Branded": "{:.1f}%"
    })
)

st.write("POI and Brand Counts - Top 30 Countries outside the US")
st.dataframe(top_30_df_styled, use_container_width=True)

#### Last 12 Months ####
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

#### Brands By Country Last 12 months ####
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

#### Overall Brands Last 12 Months ####
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


### Brand Freshness ####
# raw df
brand_freshness_grouped_df = read_from_gsheets("Brand freshness grouped")
numeric_columns = ['brand_count', 'country_brand_count', 'pct_of_brands', 'tidy_country_rank', 'country_poi_count']
brand_freshness_grouped_df[numeric_columns] = brand_freshness_grouped_df[numeric_columns].apply(pd.to_numeric)
brand_freshness_grouped_df['pct_of_brands'] = brand_freshness_grouped_df['pct_of_brands'] * 100

# pivoted table
reshaped_df = brand_freshness_grouped_df.pivot(index='tidy_country_code', columns='file_age_range', values='pct_of_brands')
reshaped_df = reshaped_df.reset_index()

# brand totals by country
brand_totals_df = brand_freshness_grouped_df.groupby(['tidy_country_code', 'tidy_country_rank']).agg({'brand_count': 'sum'}).reset_index()

# joined table
joined_df = pd.merge(brand_totals_df, reshaped_df, on='tidy_country_code', how='inner')
column_order = ['tidy_country_code', 'tidy_country_rank', 'brand_count', '0-30d', '31-60d', '61-90d', '91-120d', '120d+']
joined_df = joined_df[column_order].sort_values(by='tidy_country_rank', ascending=True).reset_index(drop=True)
joined_df["% of brand freshness < 30 days"] = joined_df["0-30d"]
joined_df["% of brand freshness < 60 days"] = joined_df["0-30d"] + joined_df["31-60d"]
joined_df["% of brand freshness < 90 days"] = joined_df["% of brand freshness < 60 days"] + joined_df["61-90d"]
joined_df = joined_df[["tidy_country_code", "brand_count", "% of brand freshness < 30 days", "% of brand freshness < 60 days", "% of brand freshness < 90 days"]]
joined_df = joined_df.rename(columns={"tidy_country_code": "Country Code", "brand_count": "Distinct Brand Count"})

joined_df_styled = (
    joined_df.style
    .apply(lambda x: ['background-color: #D7E8ED' if i % 2 == 0 else '' for i in range(len(x))], axis=0)
    .format({
        "Distinct Brand Count": "{:,.0f}",
        "% of brand freshness < 30 days": "{:.1f}%",
        "% of brand freshness < 60 days": "{:.1f}%",
        "% of brand freshness < 90 days": "{:.1f}%",
    })
)

st.dataframe(joined_df_styled, use_container_width=True)

#### Brand Freshness Top 30 ####
brand_freshness_30_df = read_from_gsheets("Brand freshness")[
    ["iso_country_code", "file_age_range", "country_poi_count", "pct_of_brands"]
]
brand_freshness_30_df["country_poi_count"] = pd.to_numeric(brand_freshness_30_df["country_poi_count"])
brand_freshness_30_df["pct_of_brands"] = pd.to_numeric(brand_freshness_30_df["pct_of_brands"])
brand_freshness_30_df["pct_of_brands"] *= 100

top_30_unique = (
    brand_freshness_30_df.sort_values("country_poi_count", ascending=False)["country_poi_count"]
    .unique()[:30]
)

brand_freshness_30_df = brand_freshness_30_df[
    brand_freshness_30_df["country_poi_count"].isin(top_30_unique)
]

brand_freshness_30_df["iso_country_code"] = pd.Categorical(
    brand_freshness_30_df["iso_country_code"],
    categories=brand_freshness_30_df["iso_country_code"].unique(),
    ordered=True,
)

brand_freshness_30_df.rename(
    columns={
        "iso_country_code": "Country Code",
        "file_age_range": "File Age Range",
        "pct_of_brands": "Percent of Brands",
    },
    inplace=True,
)

# st.dataframe(brand_freshness_30_df)

y_range = [0, 100]

brand_freshness_30 = alt.Chart(brand_freshness_30_df).mark_bar().encode(
    x=alt.X('Country Code', sort=None, title=None),
    y=alt.Y('Percent of Brands', scale=alt.Scale(domain=y_range), sort='-y'),
    color=alt.Color('File Age Range', scale=alt.Scale(domain=['120d+', '91-120d', '61-90d', '31-60d', '0-30d']))
).properties(
    width=800,
    height=400
).configure_axisX(
    labelFontSize=10,  # Set the font size of x-axis labels
    labelAngle=0
)

st.write("Brand Freshness - Top 30 Countries by Branded POI Count")
st.altair_chart(brand_freshness_30)


#### Brand Open Close #### 


brands_open_close_df = read_from_gsheets("Global Places")
brands_open_close_df = brands_open_close_df[["Country", "Release month", "Brands with at least 1 new opened POI", "Brands with at least 1 new closed POI"]]

brands_open_close_df["Brands with at least 1 new opened POI"] = brands_open_close_df["Brands with at least 1 new opened POI"].str.replace(',', '').astype(int)
brands_open_close_df["Brands with at least 1 new closed POI"] = brands_open_close_df["Brands with at least 1 new closed POI"].str.replace(',', '').astype(int)


for i, value in enumerate(brands_open_close_df['Release month']):
    try:
        brands_open_close_df.loc[i, 'Release month'] = pd.to_datetime(value, format='%b %Y').strftime('%Y-%m')
    except ValueError:
        brands_open_close_df.loc[i, 'Release month'] = pd.to_datetime(value, format='%B %Y').strftime('%Y-%m')

brands_open_close_df = brands_open_close_df[
    (pd.to_datetime(brands_open_close_df["Release month"]) >= pd.to_datetime("2021-01")) &
    (brands_open_close_df["Country"] == "Grand Total")
]

# st.dataframe(brands_open_close_df)

chart = alt.Chart(brands_open_close_df).mark_circle(size=40).encode(
    x=alt.X('Release month', title='Release month'),
    y=alt.Y('Brands with at least 1 new opened POI', title='Brands with at least 1 opening or closing of a POI'),
    color=alt.value('blue'),
    tooltip=[alt.Tooltip('Release month'),
             alt.Tooltip('Brands with at least 1 new opened POI', title='>1 Opened POI', format=',')
    ]
) + alt.Chart(brands_open_close_df).mark_circle(size=40).encode(
    x=alt.X('Release month'),
    y=alt.Y('Brands with at least 1 new closed POI'),
    color=alt.value('red'),
    tooltip=[alt.Tooltip('Release month'),
             alt.Tooltip('Brands with at least 1 new closed POI', title='>1 Closed POI', format=',')]
)

chart = chart.properties(
    width=900,
    height=500,
    title=alt.TitleParams(
        text='Brands with at Least 1 Opening or Closing of a POI',
        fontSize=18
    )
)

st.altair_chart(chart)


#### Global Brand Coverage #### 
top_1000_brands_df = (
    read_from_gsheets("Top 1000 brands")
    [["primary_brand", "naics_code", "safegraph_category", "country_code_list", "country_name_list"]]
    .sort_values("primary_brand", ascending=True)
    .reset_index(drop=True)
    .rename(columns={"primary_brand": "Brand name", "naics_code": "NAICS Code", "safegraph_category": "SafeGraph Category", "country_code_list": "Country Code", "country_name_list": "Country Name List"})
    .style.apply(lambda x: ['background-color: #D7E8ED' if i % 2 == 0 else '' for i in range(len(x))], axis=0)
)

brands_by_country_df = (
    read_from_gsheets("Countries")
    .assign(**{"Distinct brands": lambda df: df["Distinct brands"].astype(int)})
    [["iso_country_code", "country", "Distinct brands"]]
    .sort_values("Distinct brands", ascending=False)
    .rename(columns={"iso_country_code": "Country Code", "country": "Country Name"})
    [["Country Name", "Country Code", "Distinct brands"]]
    .reset_index(drop=True)
)

brands_by_country_df_styled = (
    brands_by_country_df.style
    .apply(lambda x: ['background-color: #D7E8ED' if i%2==0 else '' for i in range(len(x))], axis=0)
    .format({"Distinct brands": "{:,.0f}"})
)

brand_tab1, brand_tab2 = st.tabs(["Top 1,000 Brands", "Brand Count By Country"])

with brand_tab1:
    st.dataframe(top_1000_brands_df, use_container_width=True)

with brand_tab2:
    st.dataframe(brands_by_country_df_styled, use_container_width=True)


#### Categroy Statistics #### 
category_stats_df = read_from_gsheets("Category stats")\
    [["Country", "naics_2", "naics_code", "safegraph_category", "safegraph_subcategory", "industry_title", "total_poi_count"]]\
    .astype({'total_poi_count': int})

global_df = category_stats_df.groupby(['naics_2', 'industry_title'])\
    .agg(total_poi_count=('total_poi_count', 'sum'))\
    .sort_values('total_poi_count', ascending=False)\
    .reset_index()\
    .rename(columns={"naics_2": "2-digit NAICS", "industry_title": "Industry Title", "total_poi_count": "Total POI"})

global_df_styled = global_df.style.apply(lambda x: ['background-color: #D7E8ED' if i % 2 == 0 else '' for i in range(len(x))], axis=0)\
    .format({"Total POI": "{:,}"})

countries = ['US', 'UK', 'CA']
dfs = []

for country in countries:
    df = (
        category_stats_df[category_stats_df['Country'] == country]
        [["naics_code", "safegraph_category", "safegraph_subcategory", "total_poi_count"]]
        .rename(columns={"naics_code": "NAICS Code", "safegraph_category": "SafeGraph Category", "safegraph_subcategory": "SafeGraph Subcategory", "total_poi_count": "Total POI"})
        .sort_values('Total POI', ascending=False)
        .reset_index(drop=True)
    )

    df['Total POI'] = df['Total POI'].astype(int).apply(lambda x: "{:,}".format(x))
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


#### Fill Rates ####

columns_to_keep = ["country", "iso_country_code", "placekey", "parent_placekey", "location_name", "safegraph_brand_ids", "brands", "store_id", "naics_code", "top_category", "sub_category", "latitude", "longitude", "street_address", "city", "region", "postal_code", "phone_number", "open_hours", "category_tags", "open_on", "closed_on", "tracking_closed_since", "geometry_type", "Pct with website"]
columns_to_convert = ["placekey", "parent_placekey", "location_name", "safegraph_brand_ids", "brands", "store_id", "naics_code", "top_category", "sub_category", "latitude", "longitude", "street_address", "city", "region", "postal_code", "phone_number", "open_hours", "category_tags", "open_on", "closed_on", "tracking_closed_since", "geometry_type", "Pct with website"]
fill_rates_df = read_from_gsheets("Countries")[columns_to_keep]

for column in columns_to_convert:
    if fill_rates_df[column].dtype == object:
        fill_rates_df[column] = pd.to_numeric(fill_rates_df[column].str.replace(",", "").str.replace("%", ""), errors="coerce")
    fill_rates_df[column] *= 100
    fill_rates_df[column] = fill_rates_df[column].map("{:.0f}%".format)

fill_rates_df.rename(columns={"country": "Country", "iso_country_code": "ISO Country Code", "Pct with website": "websites"}, inplace=True)

fill_rates_df_styled = fill_rates_df.style.apply(lambda x: ['background-color: #D7E8ED' if i % 2 == 0 else '' for i in range(len(x))], axis=0)

st.write("Fill Rates")
st.dataframe(fill_rates_df_styled)

#### Carto Map ###

st.write("Visualize Global Coverage")
components.iframe("https://safegraph-data-admin.carto.com/builder/02a6ced1-4007-4659-af23-44e4eb89a436/embed", height = 600)
tier_text = ''' 
**Tier Definitions:**

`Tier 1`: These countries have seen significant investment, have gone through rigorous QA, and have naturally improved though customer feedback and time spent in market.

`Tier 2`: These countries are nearly "full scope" (coverage across all consumer oriented POIs with additional coverage in non-consumer categories). We have recently invested here and are working swiftly to close the outstanding gap and improve data quality.

`Tier 3`: We have made some investments in this country (mostly brands and select non-branded categories), but this country has not been a strong focus. We are willing to quickly turn this into a strong focus and have a critical mass starting point across consumer focused POIs.

`Tier 4`: We have some POIs here (mostly brands), but nothing super deep nor meaningful.
'''
st.markdown(tier_text)

