import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import datetime

base_api = 'https://api.covid19api.com/'
countries = requests.get(base_api + 'countries')    #get the available countries
dict_content = json.loads(countries.content)        #parse content to json string

dict_countries = {}

for d in dict_content:
    dict_countries.update({d['Country']:d['Slug']})     #update dict with country names and slugs

st.title("COVID-19 situation worldwide")
selected_country = st.sidebar.selectbox("Select the Country",list(dict_countries.keys()))
initial_date = st.sidebar.date_input("Select initial date",value=datetime.date(2020,1,1))
final_date = st.sidebar.date_input("Select final date",value=datetime.date.today())
status = st.sidebar.selectbox("Select status",['confirmed','recovered','deaths'])
initial_date = str(initial_date) + "T00:00:00Z"
final_date = str(final_date) + "T00:00:00Z"
selected_country_slug = dict_countries[selected_country]    #get the slug to use in the url

if st.sidebar.button("GO"):

    complete_url = "{0}total/country/{1}/status/{2}?from={3}&to={4}".format(base_api,selected_country_slug,status,initial_date,final_date)
    response = requests.get(complete_url)
    dict_response = json.loads(response.content)

    if len(dict_response) == 0:
        st.write("There are no records for this country!")

    else:
        df_covid = pd.DataFrame(columns=['Date', status])
        dates = []
        status_list = []
        for i in range(len(dict_response)):
            dates.append(dict_response[i]['Date'])
            status_list.append(dict_response[i]['Cases'])

        df_covid['Date'] = pd.Series(dates)
        df_covid[status] = pd.Series(status_list)

        df_covid['Date'] = pd.to_datetime(df_covid['Date'], format="%Y-%m-%d %H:%M:%S")
        df_covid.set_index('Date', inplace=True)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df_covid.index, y=df_covid[status],
            name='Cases',
            mode='markers'
        ))

        # Set options common to all traces with fig.update_traces
        fig.update_traces(mode='markers', marker_line_width=.5, marker_size=3)
        fig.update_layout(title= selected_country + " " + status + " COVID-19")

        st.plotly_chart(fig)

        st.write("Last data at " + str(df_covid.index[-1]) + ":")
        st.write(status + ": " + str(df_covid[status][-1]))

        st.write("This webapp is based on https://covid19api.com/ data.")