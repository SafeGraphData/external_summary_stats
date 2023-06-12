import streamlit as st
import pandas as pd
from read_data import read_from_gsheets

st.set_page_config(
    page_title="Brand Freshness",
    layout="wide"
)

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