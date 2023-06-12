import streamlit as st
import pandas as pd
from read_data import read_from_gsheets

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