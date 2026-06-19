#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 18:50:24 2026

@author: dina.deifallah
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path



# @st.cache_data: Streamlit reruns the entire script on every widget interaction.
# Without caching, the CSV is read from disk on every interaction — slow and wasteful.
# cache_data stores the result after the first run and reuses it until the file changes

@st.cache_data
def load_data():
    path = Path(__file__).parent.parent / 'data' / 'co2_emissions.csv'
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-01-01')
    return df

df = load_data()

st.title("CO₂ Emissions Explorer")

with st.sidebar:
    st.header("Filters")
    
    # filter 1: Multi-select country
    selected_countries = st.multiselect(
        "Countries", sorted(df['Country'].unique()),
        default=['China', 'United States', 'India', 'Germany']
    )
    
    # guard against empty country selection
    if not selected_countries:
        st.warning("Select at least one country.")
        st.stop()
          
    
    # filter 2: slider for year range - use when year is cast as an integer
    # Tuple default → two-handle range slider
    year_range = st.slider("Year range",
        int(df['Year'].min()), int(df['Year'].max()), (2010, 2020))

    # filter 3: which country to highlight in Figure 1
    # selected_countries is guaranteed non-empty here because of the st.stop()
    # guard above, so this selectbox always has at least one valid option
    highlight_country = st.selectbox(
        "Highlight country",
        selected_countries,
        index=0
    )
    
# applying filtering by country and year range 
filtered = df[
    df['Country'].isin(selected_countries) &
    (df['Year'] >= year_range[0]) &
    (df['Year'] <= year_range[1])
]

# for clarity: showing the number of countries and the number of data points selected
st.caption(f"Showing {len(selected_countries)} countries | {len(filtered)} data points")


# Figure 1: Line chart — highlight one country, grey out the rest
# FIX: a 26-colour qualitative palette is unreadable once you select more than
# ~5 countries — every line competes for attention and none of them win.
# Instead: pick ONE country to highlight in a bold colour, and render every
# other selected country in the same neutral grey. This turns the chart into
# a clear "X vs the rest" story instead of a rainbow of noise.

HIGHLIGHT_COLOR = '#E63946'   # bold red — draws the eye
GREY_COLOR      = '#BBBBBB'   # neutral grey for context lines

# Build a discrete colour map: highlighted country gets the bold colour,
# every other selected country gets the same grey
color_map = {
    country: (HIGHLIGHT_COLOR if country == highlight_country else GREY_COLOR)
    for country in selected_countries
}

fig = px.line(
    filtered, x='Year', y='CO2_Mt', color='Country',
    labels={'CO2_Mt': 'CO2 (Mt)'},
    color_discrete_map=color_map,
    category_orders={'Country': [highlight_country] + [c for c in selected_countries if c != highlight_country]},
)

# Make the highlighted line visually dominant: thicker line, drawn on top.
# Grey lines get a thinner, slightly transparent line so they recede.
for trace in fig.data:
    if trace.name == highlight_country:
        trace.update(line=dict(width=3.5, color=HIGHLIGHT_COLOR), opacity=1.0)
    else:
        trace.update(line=dict(width=1.5, color=GREY_COLOR), opacity=0.6)

fig.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    font=dict(family='Arial'),
    title=f'{highlight_country} stands out against the other {len(selected_countries)-1} selected countries',
    legend_title_text='Country',
)
st.plotly_chart(fig, use_container_width=True)
