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
    #Filter E,S,G Categories
    comps = []
    for i in esg_categories:
        X = df_company[df_company[i] == True]
        comps.append(X)
    df_company = pd.concat(comps)
    # df_company = df_company[(df_company.DATE >= start) &
    #                         (df_company.DATE <= end)]
    df_company = df_company[df_company.DATE.between(start, end)]
    return df_company