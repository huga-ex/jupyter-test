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
    df.columns = df.columns.str.strip()
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

# 7. DASHBOARD SECTIONS (Streamlit Layout Splits)
col_left, col_right = st.columns([1.1, 0.9])

with col_left:
    st.markdown("#### **Global Financials & Membership Scale**")
    
    # Financial Subplot Grid
    fig_global = make_subplots(
        rows=2, cols=1,
        row_heights=[0.5, 0.5],
        vertical_spacing=0.15,
        subplot_titles=(
            "<b>Quarterly Global Revenue Trajectory</b>", 
            "<b>Global Streaming Membership Expansion</b>"
        )
    )

    fig_global.add_trace(
        go.Scatter(
            x=filtered_df['Date'], y=filtered_df['Global Revenue'],
            mode='lines+markers', name='Global Revenue',
            line=dict(color='#E50914', width=3),
            fill='tozeroy', fillcolor='rgba(229, 9, 20, 0.08)',
            hovertemplate='<b>Date:</b> %{x|%b %Y}<br><b>Revenue:</b> $%{y:,.0f}<extra></extra>'
        ), row=1, col=1
    )

    fig_global.add_trace(
        go.Bar(
            x=filtered_df['Date'], y=filtered_df['Netflix Streaming Memberships'],
            name='Total Memberships', marker_color='#15803d', opacity=0.85,
            hovertemplate='<b>Date:</b> %{x|%b %Y}<br><b>Memberships:</b> %{y:,.0f}<extra></extra>'
        ), row=2, col=1
    )

    fig_global.update_layout(
        showlegend=False, template='plotly_white',
        height=680, margin=dict(t=40, b=40, l=60, r=40)
    )
    
    fig_global.update_xaxes(showgrid=True, gridcolor='#e2e8f0', tickformat="%b %Y", row=1, col=1)
    fig_global.update_yaxes(title_text="Revenue (USD)", showgrid=True, gridcolor='#e2e8f0', row=1, col=1)
    fig_global.update_xaxes(showgrid=True, gridcolor='#e2e8f0', tickformat="%b %Y", row=2, col=1)
    fig_global.update_yaxes(title_text="Subscribers", showgrid=True, gridcolor='#e2e8f0', row=2, col=1)

    st.plotly_chart(fig_global, use_container_width=True)

with col_right:
    st.markdown("#### **Regional Breakdown Matrix**")
    
    # Refactored Regional Matplotlib Chart -> Plotly Line Matrix
    fig_regional = go.Figure()
    
    regions = ['UCAN Members', 'EMEA Members', 'LATM Members', 'APAC Members']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'] # Enterprise color palette
    
    for r, color in zip(regions, colors):
        if r in filtered_df.columns:
            fig_regional.add_trace(
                go.Scatter(
                    x=filtered_df['Date'], 
                    y=filtered_df[r] / 1e6, 
                    mode='lines+markers',
                    name=r.replace(' Members', ''),
                    line=dict(width=2.5, color=color),
                    marker=dict(size=5),
                    hovertemplate=f'<b>Region:</b> {r.replace(" Members", "")}<br><b>Date:</b> %{{x|%b %Y}}<br><b>Subscribers:</b> %{{y:.2f}}M<extra></extra>'
                )
            )
            
    fig_regional.update_layout(
        title="<b>Regional Membership Growth</b>",
        xaxis_title="Timeline",
        yaxis_title="Members (Millions)",
        template='plotly_white',
        height=680,
        margin=dict(t=40, b=40, l=60, r=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig_regional.update_xaxes(showgrid=True, gridcolor='#e2e8f0', tickformat="%b %Y")
    fig_regional.update_yaxes(showgrid=True, gridcolor='#e2e8f0')
    
    st.plotly_chart(fig_regional, use_container_width=True)