import pandas as pd
import gspread
from google.oauth2 import service_account
import streamlit as st
import streamlit as st
from st_aggrid import AgGrid
import streamlit_shadcn_ui as ui
from local_components import card_container
from st_aggrid.grid_options_builder import GridOptionsBuilder
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
import hydralit_components as hc

# Define your Google Sheets credentials JSON file (replace with your own)
credentials_path = 'hackathon-405309-35c43230bdce.json'

# Authenticate with Google Sheets using the credentials
credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=['https://spreadsheets.google.com/feeds'])

# Authenticate with Google Sheets using gspread
gc = gspread.authorize(credentials)

# Your Google Sheets URL
url = "https://docs.google.com/spreadsheets/d/1yQXPZ4zdI8aiIzYXzzuAwDS1V_Zg0fWU6OaqZ_VmwB0/edit#gid=0"

# Open the Google Sheets spreadsheet
worksheet_1 = gc.open_by_url(url).worksheet("accounts")
worksheet_2 = gc.open_by_url(url).worksheet("targets")

#can apply customisation to almost all the properties of the card, including the progress bar
theme_bad = {'bgcolor': '#FFF0F0','title_color': 'red','content_color': 'red','icon_color': 'red', 'icon': 'fa fa-times-circle'}
theme_neutral = {'bgcolor': '#e8d5b7','title_color': 'orange','content_color': '#222831','icon_color': 'orange', 'icon': 'fa fa-question-circle'}
theme_good = {'bgcolor': '#EFF8F7','title_color': 'green','content_color': 'green','icon_color': 'green', 'icon': 'fa fa-check-circle'}

st.set_page_config(page_icon="corplogo.PNG", page_title = 'CIC_PRODUCTION ', layout="wide")

# st.sidebar.image('production_logo.png', use_column_width=True)

uploaded_file = st.sidebar.file_uploader("Upload Production Listing",  type=['csv', 'xlsx', 'xls'], kwargs=None,)


if uploaded_file is not None:
    try:
        if uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            data_types = {'Policy No': str}
            df = pd.read_excel(uploaded_file, dtype = data_types, header=6)
                      
        elif uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file, header=6)

    except Exception as e:    
        st.write("Error:", e)

if uploaded_file is not None:

    st.image('jbnp.png')
