import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import os
import time
from datetime import datetime
import pickle
import itertools
import plotly.express as px
from plot_setup import finastra_theme
from download_data import Data
import sys
import metadata_parser


#Function to filter company data
@st.cache(show_spinner=False, suppress_st_warning=True)
def filter_company_data(df_company, esg_categories, start, end):
    comps = []
    for i in esg_categories:
        X = df_company[df_company[i] == True]
        comps.append(X)
    df_company = pd.concat(comps)
    df_company = df_company[df_company.DATE.between(start, end)]
    return df_company

@st.cache(show_spinner=False,suppress_st_warning=True)
def filter_publisher(df_company,publisher):
    if publisher != 'all':
        df_company = df_company[df_company['SourceCommonName'] == publisher]
    return df_company

@st.cache(show_spinner=False, suppress_st_warning=True,allow_output_mutation=True)
def load_data(start_data, end_data):
    data = Data().read(start_data, end_data)
    companies = data["data"].Organization.sort_values().unique().tolist()
    companies.insert(0,"Select a Company")
    return data, companies

def filter_on_date(df, start, end, date_col="DATE"):
    df = df[(df[date_col] >= pd.to_datetime(start)) &
            (df[date_col] <= pd.to_datetime(end))]
    return df

def get_melted_frame(data_dict, frame_names, keepcol=None, dropcol=None):
    if keepcol:
        reduced = {k: df[keepcol].rename(k) for k, df in data_dict.items()
                   if k in frame_names}
    else:
        reduced = {k: df.drop(columns=dropcol).mean(axis=1).rename(k)
                   for k, df in data_dict.items() if k in frame_names}
    df = (pd.concat(list(reduced.values()), axis=1).reset_index().melt("date")
            .sort_values("date").ffill())
    df.columns = ["DATE", "ESG", "Score"]
    return df.reset_index(drop=True)

def get_clickable_name(url):
    try:
        T = metadata_parser.MetadataParser(url=url, search_head_only=True)
        title = T.metadata["og"]["title"].replace("|", " - ")
        return f"[{title}]({url})"
    except:
        return f"[{url}]({url})"


def main(start_data, end_data):
    #Theme
    alt.themes.register("finastra", finastra_theme)
    alt.themes.enable("finastra")
    violet, fuchsia = ["#694ED6", "#C137A2"]

    #Page setup
    icon_path = os.path.join(".", "raw", "esg_ai_logo.png")
    st.set_page_config(page_title="ESG AI", page_icon=icon_path,
                       layout='centered', initial_sidebar_state="collapsed")
    _, logo, _ = st.beta_columns(3)
    logo.image(icon_path, width=200)
    style = ("text-align:center; padding: 0px; font-family: arial black;, "
             "font-size: 400%")
    title = f"<h1 style='{style}'>ESG<sup>AI</sup></h1><br><br>"
    st.write(title, unsafe_allow_html=True)

    #Load data
    with st.spinner(text="Fetching Data..."):
        data, companies = load_data(start_data, end_data)
    df_conn = data["conn"]
    df_data = data["data"]
    embeddings = data["embed"]

    st.sidebar.title("Filter Options")
    date_place = st.sidebar.empty()
    esg_categories = st.sidebar.multiselect("Select News Categories",
                                            ["E", "S", "G"], ["E", "S", "G"])
    pub = st.sidebar.empty()
    num_neighbors = st.sidebar.slider("Number of Connections", 1, 20, value=8)

    #After company selection
    company = st.selectbox("Select a Company to Analyze", companies)
    if company and company != "Select a Company":
        df_company = df_data[df_data.Organization == company]
        diff_col = f"{company.replace(' ', '_')}_diff"
        esg_keys = ["E_score", "S_score", "G_score"]
        esg_df = get_melted_frame(data, esg_keys, keepcol=diff_col)
        ind_esg_df = get_melted_frame(data, esg_keys, dropcol="industry_tone")
        tone_df = get_melted_frame(data, ["overall_score"], keepcol=diff_col)
        ind_tone_df = get_melted_frame(data, ["overall_score"],
                                       dropcol="industry_tone")

    company = st.selectbox("Select a Company to Analyze", companies)
    if company and company != "Select a Company":
        df_company = df_data[df_data.Organization == company]
        diff_col = f"{company.replace(' ', '_')}_diff"
        esg_keys = ["E_score", "S_score", "G_score"]
        esg_df = get_melted_frame(data, esg_keys, keepcol=diff_col)
        ind_esg_df = get_melted_frame(data, esg_keys, dropcol="industry_tone")
        tone_df = get_melted_frame(data, ["overall_score"], keepcol=diff_col)
        ind_tone_df = get_melted_frame(data, ["overall_score"],
                                       dropcol="industry_tone")

        #Date UI
        start = df_company.DATE.min()
        end = df_company.DATE.max()
        selected_dates = date_place.date_input("Select a Date Range",
            value=[start, end], min_value=start, max_value=end, key=None)
        time.sleep(0.8)  
        start, end = selected_dates
        #Data filter
        df_company = filter_company_data(df_company, esg_categories,
                                         start, end)
        esg_df = filter_on_date(esg_df, start, end)
        ind_esg_df = filter_on_date(ind_esg_df, start, end)
        tone_df = filter_on_date(tone_df, start, end)
        ind_tone_df = filter_on_date(ind_tone_df, start, end)
        date_filtered = filter_on_date(df_data, start, end)





