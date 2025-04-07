import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Set title
st.title("Time Between Completion Date and Status")

# Read local CSVs (make sure these are in the same directory as this script)
hired = pd.read_csv('TP_Aged_Leads_hired.csv')
shortlisted = pd.read_csv('TP_Aged_Leads_shortlisted.csv')

# Dropdown filter
time_filter = st.selectbox(
    "Select Time Range for Analysis:",
    options=["Last 6 Months", "Last 12 Months"]
)

# Convert date columns to datetime
date_columns = ['INVITATIONDT', 'COMPLETIONDT', 'ACTIVITY_CREATED_AT', 'INSERTEDDATE', 'TERMINATIONDATE']
for col in date_columns:
    hired[col] = pd.to_datetime(hired[col], errors='coerce')
    shortlisted[col] = pd.to_datetime(shortlisted[col], errors='coerce')

# Apply time filter
today = pd.to_datetime(datetime.today())
months_back = 6 if time_filter == "Last 6 Months" else 12
date_cutoff = today - pd.DateOffset(months=months_back)

hired_filtered = hired[hired['COMPLETIONDT'] >= date_cutoff]
shortlisted_filtered = shortlisted[shortlisted['COMPLETIONDT'] >= date_cutoff]

# Define binning function
def categorize_days_diff(df):
    days_diff = (df['COMPLETIONDT'] - df['INSERTEDDATE']).dt.days.abs()
    bins = [-1, 0, 3, 7, 9, float('inf')]
    labels = ['Less than 1 day', '1-3 days', '4-7 days', '7-9 days', 'More than 9 days']
    return pd.cut(days_diff, bins=bins, labels=labels)

# Shortlisted graph
shortlisted_filtered['Time_Category'] = categorize_days_diff(shortlisted_filtered)
shortlisted_counts = shortlisted_filtered['Time_Category'].value_counts().reindex(
    ['Less than 1 day', '1-3 days', '4-7 days', '7-9 days', 'More than 9 days']
).fillna(0)

fig_shortlisted = px.bar(
    x=shortlisted_counts.index,
    y=shortlisted_counts.values,
    text=shortlisted_counts.values,
    labels={'x': 'Time Range', 'y': 'Count'},
    title=f'Amount of time b/w Completion date and Shortlisted ({time_filter})'
)
fig_shortlisted.update_traces(textposition='outside')
st.plotly_chart(fig_shortlisted)

# Hired graph
hired_filtered['Time_Category'] = categorize_days_diff(hired_filtered)
hired_counts = hired_filtered['Time_Category'].value_counts().reindex(
    ['Less than 1 day', '1-3 days', '4-7 days', '7-9 days', 'More than 9 days']
).fillna(0)

fig_hired = px.bar(
    x=hired_counts.index,
    y=hired_counts.values,
    text=hired_counts.values,
    labels={'x': 'Time Range', 'y': 'Count'},
    title=f'Amount of time b/w Completion date and Hired ({time_filter})'
)
fig_hired.update_traces(textposition='outside')
st.plotly_chart(fig_hired)
