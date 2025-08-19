import streamlit as st
import pandas as pd
import altair as alt
import requests
import json
import os
from datetime import datetime, timedelta

# Configure Streamlit page
st.set_page_config(
    page_title="Financial Telegram Monitor",
    page_icon="📊",
    layout="wide"
)

# API base URL (adjust if needed)
API_BASE_URL = "http://localhost:8000/api/risk"

def load_local_data():
    """Load data from local JSON files if API is not available."""
    data_dir = os.path.join(os.path.dirname(__file__), '../../data/raw')
    all_messages = []
    
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(data_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        messages = json.load(f)
                        all_messages.extend(messages)
                except Exception:
                    continue
    
    return pd.DataFrame(all_messages)

def get_risky_messages():
    """Fetch risky messages from API or local data."""
    try:
        response = requests.get(f"{API_BASE_URL}/risky_messages", timeout=5)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
    except:
        pass
    
    # Fallback to local data
    df = load_local_data()
    if not df.empty:
        # Simple risk scoring for demo
        df['risk_score'] = df['text'].str.len() / 1000  # Placeholder
        return df.head(10)
    
    return pd.DataFrame()

def get_trending_products():
    """Fetch trending products from API or local data."""
    try:
        response = requests.get(f"{API_BASE_URL}/trending_products", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    # Fallback to local data
    df = load_local_data()
    if not df.empty and 'mentions' in df.columns:
        product_counts = {}
        for mentions in df['mentions'].dropna():
            for product in mentions:
                product_counts[product] = product_counts.get(product, 0) + 1
        
        trending = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        return {"trending_products": [{"product": k, "mentions": v} for k, v in trending]}
    
    return {"trending_products": []}

def get_channel_stats():
    """Fetch channel statistics from API or local data."""
    try:
        response = requests.get(f"{API_BASE_URL}/channel_stats", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    # Fallback to local data
    df = load_local_data()
    if not df.empty and 'channel' in df.columns:
        stats = df.groupby('channel').agg({
            'id': 'count',
            'text': lambda x: len([t for t in x if len(t) > 100])  # Placeholder for high-risk
        }).rename(columns={'id': 'total_messages', 'text': 'high_risk_messages'})
        
        return {"channel_statistics": stats.to_dict('index')}
    
    return {"channel_statistics": {}}

def main():
    st.title("📊 Financial Telegram Monitor Dashboard")
    st.markdown("Real-time monitoring and risk analysis of financial/medical Telegram channels")
    
    # Sidebar
    st.sidebar.header("Controls")
    auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=False)
    
    if auto_refresh:
        st.rerun()
    
    # Main dashboard
    col1, col2, col3 = st.columns(3)
    
    # Key metrics
    with col1:
        st.metric("Monitored Channels", "3", delta="0")
    
    with col2:
        st.metric("Messages Today", "127", delta="+23")
    
    with col3:
        st.metric("High Risk Alerts", "8", delta="+2")
    
    st.divider()
    
    # Risk Messages Table
    st.subheader("🚨 High Risk Messages")
    risky_df = get_risky_messages()
    
    if not risky_df.empty:
        # Display table with risk scores
        display_df = risky_df[['channel', 'text', 'date']].copy()
        if 'risk_score' in risky_df.columns:
            display_df['risk_score'] = risky_df['risk_score'].round(3)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=300
        )
    else:
        st.info("No high-risk messages found or API unavailable")
    
    # Two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Trending Products")
        trending_data = get_trending_products()
        
        if trending_data["trending_products"]:
            trend_df = pd.DataFrame(trending_data["trending_products"])
            
            chart = alt.Chart(trend_df).mark_bar().encode(
                x=alt.X('mentions:Q', title='Mentions'),
                y=alt.Y('product:N', sort='-x', title='Product'),
                color=alt.Color('mentions:Q', scale=alt.Scale(scheme='blues'))
            ).properties(
                height=300,
                title="Most Mentioned Products (Last 7 Days)"
            )
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No trending products data available")
    
    with col2:
        st.subheader("📊 Channel Statistics")
        channel_data = get_channel_stats()
        
        if channel_data["channel_statistics"]:
            stats_df = pd.DataFrame.from_dict(
                channel_data["channel_statistics"], 
                orient='index'
            ).reset_index()
            stats_df.columns = ['Channel', 'Total Messages', 'High Risk Messages', 'Avg Risk Score']
            
            st.dataframe(
                stats_df,
                use_container_width=True,
                height=300
            )
        else:
            st.info("No channel statistics available")
    
    # Risk Analysis Tool
    st.divider()
    st.subheader("🔍 Message Risk Analyzer")
    
    user_message = st.text_area(
        "Enter a message to analyze for risk factors:",
        placeholder="Type or paste a message here..."
    )
    
    if st.button("Analyze Risk") and user_message:
        try:
            response = requests.post(
                f"{API_BASE_URL}/detect",
                json={
                    "message_text": user_message,
                    "authorized": True
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    risk_color = "red" if result["risk_score"] >= 0.7 else "orange" if result["risk_score"] >= 0.4 else "green"
                    st.metric(
                        "Risk Score", 
                        f"{result['risk_score']:.3f}",
                        delta=f"Level: {result['risk_level']}"
                    )
                
                with col2:
                    st.metric("Confidence", f"{result['confidence']:.3f}")
                
                with col3:
                    st.metric("Products Detected", len(result['detected_products']))
                
                if result['detected_products']:
                    st.write("**Detected Products:**", ", ".join(result['detected_products']))
                
                if result['risk_factors']:
                    st.write("**Risk Factors:**", ", ".join(result['risk_factors']))
            
            else:
                st.error("Failed to analyze message")
                
        except Exception as e:
            st.error(f"Error connecting to API: {str(e)}")
    
    # Footer
    st.divider()
    st.markdown("*Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "*")

if __name__ == "__main__":
    main()
