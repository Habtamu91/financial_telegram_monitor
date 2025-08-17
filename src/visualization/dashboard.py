# In src/visualization/dashboard.py
import streamlit as st

def show_risk_heatmap():
    st.altair_chart(create_risk_visualization(), 
                   use_container_width=True)
    
def create_risk_visualization():
    # Uses your fct_risk_indicators data
    return alt.Chart(risk_data).mark_rect().encode(
        x='channel:T',
        y='day:T',
        color='mean(risk_score):Q'
    )