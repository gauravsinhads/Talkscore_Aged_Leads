import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide")
st.title("Aged Leads Dashboard")

# Read local CSVs
hired = pd.read_csv('TP_Aged_Leads_hired.csv')
shortlisted = pd.read_csv('TP_Aged_Leads_shortlisted.csv')

# Convert datetime columns
common_date_cols = ['INVITATIONDT', 'COMPLETIONDT', 'ACTIVITY_CREATED_AT', 'INSERTEDDATE']
for col in common_date_cols:
    hired[col] = pd.to_datetime(hired[col], errors='coerce')
    shortlisted[col] = pd.to_datetime(shortlisted[col], errors='coerce')

hired['TERMINATIONDATE'] = pd.to_datetime(hired['TERMINATIONDATE'], errors='coerce')

# WORKLOCATION filter
all_locations = sorted(set(hired['WORKLOCATION'].dropna().unique()).union(
    shortlisted['WORKLOCATION'].dropna().unique()
))
selected_location = st.selectbox("Select WORKLOCATION:", options=["All"] + all_locations)

# Apply location filter
if selected_location != "All":
    hired = hired[hired['WORKLOCATION'] == selected_location]
    shortlisted = shortlisted[shortlisted['WORKLOCATION'] == selected_location]

# Time range dropdown
time_filter = st.selectbox("Select Time Range for Analysis:", options=["Last 6 Months", "Last 12 Months"])
months_back = 6 if time_filter == "Last 6 Months" else 12
date_cutoff = pd.to_datetime(datetime.today()) - pd.DateOffset(months=months_back)

# Apply date filtering
hired_filtered = hired[hired['COMPLETIONDT'] >= date_cutoff]
shortlisted_filtered = shortlisted[shortlisted['COMPLETIONDT'] >= date_cutoff]

# Categorize time between COMPLETIONDT and INSERTEDDATE
def categorize_days_diff(df):
    days_diff = (df['COMPLETIONDT'] - df['INSERTEDDATE']).dt.days.abs()
    bins = [-1, 0, 3, 7, 9, float('inf')]
    labels = ['Less than 1 day', '1-3 days', '4-7 days', '7-9 days', 'More than 9 days']
    return pd.cut(days_diff, bins=bins, labels=labels)

# ---- Shortlisted Graph ----
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
st.plotly_chart(fig_shortlisted, use_container_width=True)

# ---- Hired Graph ----
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
st.plotly_chart(fig_hired, use_container_width=True)

# ---- Employment Duration Graph ----
def categorize_employment(df):
    terminated = df[
        (df['EMPLOYMENTSTATUS'] == 'Terminated') &
        df['TERMINATIONDATE'].notna() &
        df['INSERTEDDATE'].notna()
    ].copy()

    terminated['Duration_Days'] = (terminated['TERMINATIONDATE'] - terminated['INSERTEDDATE']).dt.days
    bins = [-1, 30, 60, 90, float('inf')]
    labels = ['0-30 Days', '31-60 Days', '61-90 Days', '90 Days and More']
    terminated['Category'] = pd.cut(terminated['Duration_Days'], bins=bins, labels=labels)
    term_counts = terminated['Category'].value_counts().reindex(labels, fill_value=0)

    active_dormant_count = df[df['EMPLOYMENTSTATUS'].isin(['Active', 'Dormant'])].shape[0]
    result = term_counts.to_dict()
    result['Active & Dormant'] = active_dormant_count

    return result

employment_counts = categorize_employment(hired_filtered)

fig_employment = px.bar(
    x=list(employment_counts.values()),
    y=list(employment_counts.keys()),
    orientation='h',
    text=list(employment_counts.values()),
    labels={'x': 'Count', 'y': 'Employment Duration'},
    title='Employment Duration Status (Hired)'
)
fig_employment.update_traces(textposition='outside')
fig_employment.update_layout(yaxis={'categoryorder':'array', 'categoryarray': [
    '0-30 Days', '31-60 Days', '61-90 Days', '90 Days and More', 'Active & Dormant'
]})
st.plotly_chart(fig_employment, use_container_width=True)
