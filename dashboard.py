import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(
    page_title="IPL 2025 Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    .stMetric label {
        color: #262730 !important;
        font-weight: 600 !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #262730 !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    .stMetric [data-testid="stMetricDelta"] {
        color: #1f77b4 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Load Data
batters = pd.read_csv("IPL2025Batters.csv")
bowlers = pd.read_csv("IPL2025Bowlers.csv")

# Convert numeric columns to proper types
batters['AVG'] = pd.to_numeric(batters['AVG'], errors='coerce')
batters['SR'] = pd.to_numeric(batters['SR'], errors='coerce')
batters['Runs'] = pd.to_numeric(batters['Runs'], errors='coerce')
bowlers['AVG'] = pd.to_numeric(bowlers['AVG'], errors='coerce')
bowlers['ECO'] = pd.to_numeric(bowlers['ECO'], errors='coerce')
bowlers['WKT'] = pd.to_numeric(bowlers['WKT'], errors='coerce')

# Create All-Rounder DataFrame (players in both datasets)
all_rounders = pd.merge(
    batters[['Player Name', 'Runs', 'SR', 'AVG']],
    bowlers[['Player Name', 'WKT', 'ECO']],
    on='Player Name',
    how='inner'
)

# Calculate All-Rounder Score (weighted combination of batting and bowling)
all_rounders['AR_Score'] = (
    (all_rounders['Runs'] / all_rounders['Runs'].max() * 50) +
    (all_rounders['WKT'] / all_rounders['WKT'].max() * 50)
)

# Title Section
st.markdown("<h1 style='text-align: center; color: #FF6B35;'>🏏 IPL 2025 Performance Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar Filters
st.sidebar.header("⚙️ Filters")
top_n = st.sidebar.slider("Select Top N Players", 5, 20, 10)

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Runs", f"{batters['Runs'].sum():,.0f}", "🔥")
with col2:
    st.metric("Total Wickets", f"{bowlers['WKT'].sum():.0f}", "🎯")
with col3:
    st.metric("Highest Score", f"{batters['Runs'].max():.0f}", f"by {batters.loc[batters['Runs'].idxmax(), 'Player Name']}")
with col4:
    st.metric("Most Wickets", f"{bowlers['WKT'].max():.0f}", f"by {bowlers.loc[bowlers['WKT'].idxmax(), 'Player Name']}")

st.markdown("---")

# Top Batters Section with Horizontal Bar Chart
st.subheader("🔥 Top Run Scorers")
top_batters = batters.sort_values("Runs", ascending=False).head(top_n)
fig1 = px.bar(
    top_batters,
    y="Player Name",
    x="Runs",
    orientation='h',
    color="Runs",
    color_continuous_scale="Reds",
    title=f"Top {top_n} Run Scorers",
    labels={"Player Name": "Player", "Runs": "Total Runs"},
    text="Runs"
)
fig1.update_traces(texttemplate='%{text:.0f}', textposition='outside')
fig1.update_layout(height=400, showlegend=False, yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig1, width='stretch')

# Two Column Layout for Batting Stats
col1, col2 = st.columns(2)

with col1:
    st.subheader("⚡ Best Strike Rates")
    best_sr = batters.dropna(subset=['SR']).sort_values("SR", ascending=False).head(top_n)
    fig2 = px.bar(
        best_sr,
        y="Player Name",
        x="SR",
        orientation='h',
        color="SR",
        color_continuous_scale="Blues",
        labels={"Player Name": "Player", "SR": "Strike Rate"},
        text="SR"
    )
    fig2.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig2.update_layout(height=400, showlegend=False, yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig2, width='stretch')

with col2:
    st.subheader("🎯 Best Averages")
    best_avg = batters.dropna(subset=['AVG'])
    best_avg = best_avg[best_avg['AVG'] > 0].sort_values("AVG", ascending=False).head(top_n)
    fig3 = px.bar(
        best_avg,
        y="Player Name",
        x="AVG",
        orientation='h',
        color="AVG",
        color_continuous_scale="Greens",
        labels={"Player Name": "Player", "AVG": "Average"},
        text="AVG"
    )
    fig3.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig3.update_layout(height=400, showlegend=False, yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig3, width='stretch')

st.markdown("---")

# All-Rounder Performance Section
st.subheader("🌟 Best All-Round Performances")
top_all_rounders = all_rounders.sort_values("AR_Score", ascending=False).head(top_n)

# Create a grouped bar chart for All-Rounders
fig_ar = go.Figure()

fig_ar.add_trace(go.Bar(
    y=top_all_rounders['Player Name'],
    x=top_all_rounders['Runs'],
    name='Runs',
    orientation='h',
    marker=dict(color='#FF6B6B'),
    text=top_all_rounders['Runs'],
    textposition='outside'
))

fig_ar.add_trace(go.Bar(
    y=top_all_rounders['Player Name'],
    x=top_all_rounders['WKT'] * 30,  # Scale wickets for visibility
    name='Wickets (x30)',
    orientation='h',
    marker=dict(color='#4ECDC4'),
    text=top_all_rounders['WKT'],
    textposition='outside'
))

fig_ar.update_layout(
    title=f"Top {top_n} All-Rounders (Runs + Wickets)",
    xaxis_title="Performance Metric",
    yaxis_title="Player",
    barmode='group',
    height=500,
    showlegend=True,
    yaxis={'categoryorder':'total ascending'}
)

st.plotly_chart(fig_ar, width='stretch')

# All-Rounder Stats Table
st.subheader("📊 All-Rounder Statistics")
ar_display = top_all_rounders[['Player Name', 'Runs', 'SR', 'WKT', 'ECO']].copy()
ar_display.columns = ['Player', 'Runs', 'Strike Rate', 'Wickets', 'Economy']
ar_display = ar_display.round(2)
st.dataframe(ar_display, hide_index=True, use_container_width=True)

st.markdown("---")

# Top Bowlers Section
st.subheader("🎯 Top Wicket Takers")
top_bowlers = bowlers.sort_values("WKT", ascending=False).head(top_n)
fig4 = px.bar(
    top_bowlers,
    y="Player Name",
    x="WKT",
    orientation='h',
    color="WKT",
    color_continuous_scale="Purples",
    title=f"Top {top_n} Wicket Takers",
    labels={"Player Name": "Player", "WKT": "Wickets"},
    text="WKT"
)
fig4.update_traces(texttemplate='%{text:.0f}', textposition='outside')
fig4.update_layout(height=400, showlegend=False, yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig4, width='stretch')

# Two Column Layout for Bowling Stats
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Best Economy Rates")
    best_eco = bowlers.dropna(subset=['ECO'])
    best_eco = best_eco[best_eco['ECO'] > 0].sort_values("ECO", ascending=True).head(top_n)
    fig5 = px.bar(
        best_eco,
        y="Player Name",
        x="ECO",
        orientation='h',
        color="ECO",
        color_continuous_scale="Oranges_r",
        labels={"Player Name": "Player", "ECO": "Economy Rate"},
        text="ECO"
    )
    fig5.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig5.update_layout(height=400, showlegend=False, yaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig5, width='stretch')

with col2:
    st.subheader("🎪 Best Bowling Averages")
    best_bowl_avg = bowlers.dropna(subset=['AVG'])
    best_bowl_avg = best_bowl_avg[best_bowl_avg['AVG'] > 0].sort_values("AVG", ascending=True).head(top_n)
    fig6 = px.bar(
        best_bowl_avg,
        y="Player Name",
        x="AVG",
        orientation='h',
        color="AVG",
        color_continuous_scale="Teal_r",
        labels={"Player Name": "Player", "AVG": "Bowling Average"},
        text="AVG"
    )
    fig6.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig6.update_layout(height=400, showlegend=False, yaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig6, width='stretch')

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>IPL 2025 Analytics Dashboard | Data Visualization</p>", unsafe_allow_html=True)