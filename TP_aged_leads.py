
import streamlit as st
import pandas as pd
import plotly.express as px

# Set the title
st.title("Time Between Completion Date and Status")

# Upload CSV files
hired_file = st.file_uploader("Upload TP_Aged_Leads_hired.csv", type=["csv"])
shortlisted_file = st.file_uploader("Upload TP_Aged_Leads_shortlisted.csv", type=["csv"])

if hired_file and shortlisted_file:
    # Read CSVs
    hired = pd.read_csv(hired_file)
    shortlisted = pd.read_csv(shortlisted_file)

    # Convert columns to datetime
    date_columns = ['INVITATIONDT', 'COMPLETIONDT', 'ACTIVITY_CREATED_AT', 'INSERTEDDATE', 'TERMINATIONDATE']
    for col in date_columns:
        hired[col] = pd.to_datetime(hired[col], errors='coerce')
        shortlisted[col] = pd.to_datetime(shortlisted[col], errors='coerce')

    # Define binning function
    def categorize_days_diff(df):
        days_diff = (df['COMPLETIONDT'] - df['INSERTEDDATE']).dt.days.abs()
        bins = [-1, 0, 3, 7, 9, float('inf')]
        labels = ['Less than 1 day', '1-3 days', '4-7 days', '7-9 days', 'More than 9 days']
        return pd.cut(days_diff, bins=bins, labels=labels)

    # Process shortlisted
    shortlisted['Time_Category'] = categorize_days_diff(shortlisted)
    shortlisted_counts = shortlisted['Time_Category'].value_counts().reindex(
        ['Less than 1 day', '1-3 days', '4-7 days', '7-9 days', 'More than 9 days']
    ).fillna(0)

    # Plot for shortlisted
    fig_shortlisted = px.bar(
        x=shortlisted_counts.index,
        y=shortlisted_counts.values,
        text=shortlisted_counts.values,
        labels={'x': 'Time Range', 'y': 'Count'},
        title='Amount of time b/w Completion date and Shortlisted'
    )
    fig_shortlisted.update_traces(textposition='outside')
    st.plotly_chart(fig_shortlisted)

    # Process hired
    hired['Time_Category'] = categorize_days_diff(hired)
    hired_counts = hired['Time_Category'].value_counts().reindex(
        ['Less than 1 day', '1-3 days', '4-7 days', '7-9 days', 'More than 9 days']
    ).fillna(0)

    # Plot for hired
    fig_hired = px.bar(
        x=hired_counts.index,
        y=hired_counts.values,
        text=hired_counts.values,
        labels={'x': 'Time Range', 'y': 'Count'},
        title='Amount of time b/w Completion date and Hired'
    )
    fig_hired.update_traces(textposition='outside')
    st.plotly_chart(fig_hired)

else:
    st.info("Please upload both CSV files to see the dashboard.")
