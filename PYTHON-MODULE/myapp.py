# siderbar filter
#KPI
#Data tables
#Charts
#numpy data
#session state
#metric
#tabs
#Download button


import streamlit as st
import pandas as pd
import numpy as np


# page config

st.set_page_config(
    page_title="Qutantam-Vector-dashboard",
    page_icon="📊",
    layout="wide"
)


st.sidebar.title("⚙️ Dashboard utilis")

department = st.sidebar.multiselect(
    "Select the department",
    [
        "Engineering","HR","Finance","Sales"
    ],
    default=["Engineering"]
)

employee_count = st.sidebar.slider(
    "Number of employee",
    50,
    100,
    200
)