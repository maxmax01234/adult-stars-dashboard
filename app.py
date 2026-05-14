import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import plotly.express as px
import time
from datetime import datetime

st.set_page_config(page_title="🔥 Adult Stars Live Dashboard", layout="wide", initial_sidebar_state="expanded")

# Dark sexy theme
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .metric-card { background-color: #1e2530; padding: 20px; border-radius: 10px; }
    h1 { color: #ff4b8f; }
</style>
""", unsafe_allow_html=True)

st.title("🔥 Adult Stars Realtime Dashboard")
st.markdown(f"**Last refreshed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

@st.cache_data(ttl=300)  # Cache for 5 minutes
def scrape_pornhub_top():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0 Safari/537.36"
        }
        url = "https://www.pornhub.com/pornstars/top"
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        stars = []
        # Adjust selectors if Pornhub changes structure
        rows = soup.select("li[data-id]") or soup.select(".pornstarList li")
        
        for item in rows[:50]:  # Top 50
            try:
                name_tag = item.find('a', href=True)
                name = name_tag.get_text(strip=True) if name_tag else "N/A"
                
                views_tag = item.find(text=lambda t: t and ("View" in t or "M" in t or "B" in t))
                views = views_tag.strip() if views_tag else "N/A"
                
                videos = "N/A"
                rank = len(stars) + 1
                
                stars.append({
                    "Rank": rank,
                    "Pornstar": name,
                    "Total Views": views,
                    "Videos": videos,
                    "Source": "Pornhub"
                })
            except:
                continue
                
        return pd.DataFrame(stars)
    except Exception as e:
        st.error(f"Scraping failed: {e}")
        # Fallback mock data
        return pd.DataFrame({
            "Rank": range(1, 21),
            "Pornstar": ["Alex Adams", "Abella Danger", "Lana Rhoades", "Angela White", "Violet Myers"] * 4,
            "Total Views": ["572M", "285M", "390M", "256M", "183M"] * 4,
            "Videos": [547, 501, 339, 513, 402] * 4,
            "Source": ["Pornhub"] * 20
        })

# Load data
df = scrape_pornhub_top()

# KPIs
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Stars Tracked", len(df), "Top 50")
with col2:
    st.metric("Leading Star", df.iloc[0]["Pornstar"] if not df.empty else "N/A")
with col3:
    st.metric("Last Update", "Live (every 5 min)")

# Main table
st.subheader("🏆 Top Pornstars by Views (Pornhub)")
st.dataframe(
    df.style.background_gradient(cmap='RdPu', subset=["Rank"]),
    use_container_width=True,
    hide_index=True
)

# Charts
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Top 15 by Rank")
    fig = px.bar(df.head(15), x="Pornstar", y="Rank", 
                 title="Top 15 - Lower Rank = Better",
                 color="Rank", color_continuous_scale="pink")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("View Distribution (Top 20)")
    top20 = df.head(20).copy()
    # Simple numeric conversion for demo
    top20["Views_Num"] = top20["Total Views"].str.replace("M", "000000").str.replace("B", "000000000").str.extract(r'(\d+)').astype(float)
    fig2 = px.pie(top20, names="Pornstar", values="Views_Num", title="Share of Spotlight")
    st.plotly_chart(fig2, use_container_width=True)

# Auto-refresh
if st.button("🔄 Manual Refresh"):
    st.cache_data.clear()
    st.rerun()

st.caption("Auto-refreshes every 5 minutes • Built with Streamlit • For educational/entertainment use")

st.markdown("---")
st.info("**Note:** Web scraping can break if sites change. For more reliable/long-term use, consider Apify actors for Pornhub scraping.")