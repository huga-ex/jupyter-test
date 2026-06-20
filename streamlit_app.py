import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# 1. APPLICATION & PAGE CONFIGURATION
st.set_page_config(
    page_title="Netflix Executive Performance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. DATA LOAD ENGINE
@st.cache_data
def load_data():
    df = pd.read_csv('netflix_revenue_updated.csv')
    # df.columns = df.columns.str.strip()
    df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
    return df

df = load_data()

# 3. EXECUTIVE SIDEBAR CONTROLS
st.sidebar.header("Dashboard Controls")
date_range = st.sidebar.slider(
    "Select Reporting Timeline",
    min_value=df['Date'].min().to_pydatetime(),
    max_value=df['Date'].max().to_pydatetime(),
    value=(df['Date'].min().to_pydatetime(), df['Date'].max().to_pydatetime()),
    format="MMM YYYY"
)

# Filter dataset dynamically based on UI selection
filtered_df = df[(df['Date'] >= date_range[0]) & (df['Date'] <= date_range[1])]

# 4. BUSINESS METRIC EVALUATION (KPIs)
latest_revenue = filtered_df['Global Revenue'].iloc[-1] / 1e9 if not filtered_df.empty else 0
init_mem = filtered_df['Netflix Streaming Memberships'].iloc[0] / 1e6 if not filtered_df.empty else 1
final_mem = filtered_df['Netflix Streaming Memberships'].iloc[-1] / 1e6 if not filtered_df.empty else 1
mem_growth = ((final_mem - init_mem) / init_mem) * 100

# 5. HEADER ZONE
st.title("Netflix Key Performance Indicators")
st.markdown("### *Executive Dashboard View*")
st.write("---")

# 6. STREAMLIT KPI BANNER CONTAINER
kpi_col1, kpi_col2 = st.columns(2)

with kpi_col1:
    st.metric(
        label="Latest Peak Revenue", 
        value=f"${latest_revenue:.2f} B", 
        delta=f"As of {filtered_df['Date'].dt.strftime('%b %Y').iloc[-1]}" if not filtered_df.empty else None
    )

with kpi_col2:
    st.metric(
        label="Membership Growth", 
        value=f"+{mem_growth:.1f}%", 
        delta=f"{init_mem:.1f}M → {final_mem:.1f}M Subscribers"
    )

st.write("---")

# -------------------------------------------------------------------------
# 7. ROW 1: SIDE-BY-SIDE GLOBAL METRICS (TWO COLUMNS)
# -------------------------------------------------------------------------
row1_col1, row1_col2 = st.columns([1, 1])

# --- Left Column: Graph 1 (Revenue) ---
with row1_col1:
    fig_rev = go.Figure()
    fig_rev.add_trace(
        go.Scatter(
            x=filtered_df['Date'], y=filtered_df['Global Revenue'],
            mode='lines+markers', name='Global Revenue',
            line=dict(color='#E50914', width=3),
            fill='tozeroy', fillcolor='rgba(229, 9, 20, 0.08)',
            hovertemplate='<b>Date:</b> %{x|%b %Y}<br><b>Revenue:</b> $%{y:,.0f}<extra></extra>'
        )
    )
    fig_rev.update_layout(
        title="<b>1. Quarterly Global Revenue Trajectory</b>",
        template='plotly_white', height=400, margin=dict(t=40, b=40, l=60, r=40),
        showlegend=False
    )
    fig_rev.update_xaxes(showgrid=True, gridcolor='#e2e8f0', tickformat="%b %Y")
    fig_rev.update_yaxes(title_text="Revenue (USD)", showgrid=True, gridcolor='#e2e8f0')
    
    st.plotly_chart(fig_rev, width='stretch')

# --- Right Column: Graph 2 (Memberships) ---
with row1_col2:
    fig_mem = go.Figure()
    fig_mem.add_trace(
        go.Bar(
            x=filtered_df['Date'], y=filtered_df['Netflix Streaming Memberships'],
            name='Total Memberships', marker_color='#15803d', opacity=0.85,
            hovertemplate='<b>Date:</b> %{x|%b %Y}<br><b>Memberships:</b> %{y:,.0f}<extra></extra>'
        )
    )
    fig_mem.update_layout(
        title="<b>2. Global Streaming Membership Expansion</b>",
        template='plotly_white', height=400, margin=dict(t=40, b=40, l=60, r=40),
        showlegend=False
    )
    fig_mem.update_xaxes(showgrid=True, gridcolor='#e2e8f0', tickformat="%b %Y")
    fig_mem.update_yaxes(title_text="Subscribers", showgrid=True, gridcolor='#e2e8f0')
    
    st.plotly_chart(fig_mem, width='stretch')


# -------------------------------------------------------------------------
# 8. ROW 2: REGIONAL BREAKDOWN (FULL WIDTH)
# -------------------------------------------------------------------------
st.write("---")  # Structural section divider

fig_regional = go.Figure()
regions = ['UCAN Members', 'EMEA Members', 'LATM Members', 'APAC Members']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
for r, color in zip(regions, colors):
    if r in filtered_df.columns:
        fig_regional.add_trace(
            go.Scatter(
                x=filtered_df['Date'], y=filtered_df[r] / 1e6, 
                mode='lines+markers', name=r.replace(' Members', ''),
                line=dict(width=2.5, color=color), marker=dict(size=5),
                hovertemplate=f'<b>Region:</b> {r.replace(" Members", "")}<br><b>Date:</b> %{{x|%b %Y}}<br><b>Subscribers:</b> %{{y:.2f}}M<extra></extra>'
            )
        )
        
fig_regional.update_layout(
    title="<b>3. Regional Membership Growth</b>",
    xaxis_title="Timeline", yaxis_title="Members (Millions)",
    template='plotly_white', height=500, margin=dict(t=40, b=40, l=60, r=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
fig_regional.update_xaxes(showgrid=True, gridcolor='#e2e8f0', tickformat="%b %Y")
fig_regional.update_yaxes(showgrid=True, gridcolor='#e2e8f0')

# This call sits outside of columns, forcing it to span 100% layout width
st.plotly_chart(fig_regional, width='stretch')
