import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="GB Bicycle Accidents 1979–2018",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Constants ─────────────────────────────────────────────────────────────────
DAY_ORDER      = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
MONTH_ORDER    = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
SEVERITY_ORDER = ["Slight","Serious","Fatal"]
AGE_ORDER      = ["6 to 10","11 to 15","16 to 20","21 to 25","26 to 35",
                  "36 to 45","46 to 55","56 to 65","66 to 75"]
SEV_COLORS     = {"Slight":"#2196F3","Serious":"#FF9800","Fatal":"#F44336"}
GEN_COLORS     = {"Male":"#1976D2","Female":"#E91E63","Other":"#9E9E9E"}

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    accidents = pd.read_csv("Accidents.csv")
    bikers    = pd.read_csv("Bikers.csv")
    df = pd.merge(bikers, accidents, on="Accident_Index", how="left")
    df = df.dropna(subset=["Date"])
    df["Date"]        = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"]        = df["Date"].dt.year.astype(int)
    df["Month"]       = df["Date"].dt.month.astype(int)
    df["Month_Name"]  = df["Date"].dt.strftime("%b")
    df["Hour"]        = pd.to_datetime(df["Time"], format="%H:%M", errors="coerce").dt.hour
    df["Speed_limit"] = df["Speed_limit"].astype(int)
    df["Road_type"]   = df["Road_type"].str.replace("One way sreet", "One way street", regex=False)
    df["Is_Fatal"]    = (df["Severity"] == "Fatal").astype(int)
    df["Is_SF"]       = df["Severity"].isin(["Fatal","Serious"]).astype(int)
    return df

df_full = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🚲 Filters")
    st.caption("All filters apply across every tab.")

    year_range = st.slider(
        "Year Range",
        int(df_full["Year"].min()), int(df_full["Year"].max()),
        (int(df_full["Year"].min()), int(df_full["Year"].max())),
    )
    severity_sel = st.multiselect("Injury Severity", SEVERITY_ORDER, default=SEVERITY_ORDER)
    all_genders  = sorted(df_full["Gender"].dropna().unique())
    gender_sel   = st.multiselect("Gender", all_genders, default=all_genders)
    all_roads    = sorted(df_full["Road_conditions"].dropna().unique())
    road_cond_sel= st.multiselect("Road Conditions", all_roads, default=all_roads)

    st.divider()
    st.caption("Dataset: 827,861 cyclist records\nGreat Britain · 1979–2018\nALY 6110 – Assignment 1")

# Apply filters
mask = (
    df_full["Year"].between(*year_range)
    & df_full["Severity"].isin(severity_sel)
    & df_full["Gender"].isin(gender_sel)
    & df_full["Road_conditions"].isin(road_cond_sel)
)
df = df_full[mask]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🚲 Bicycle Accidents in Great Britain (1979–2018)")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_overview, tab_temporal, tab_severity, tab_demo, tab_env, tab_risk = st.tabs([
    "📊 Overview",
    "📅 Temporal Trends",
    "⚠️ Severity",
    "👥 Demographics",
    "🌦️ Environment & Roads",
    "📈 Risk Analysis",
])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 – OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
with tab_overview:
    total       = len(df)
    fatal_pct   = df["Severity"].eq("Fatal").mean() * 100
    serious_pct = df["Severity"].eq("Serious").mean() * 100
    unique_acc  = df["Accident_Index"].nunique()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Records",     f"{total:,}")
    c2.metric("Unique Accidents",  f"{unique_acc:,}")
    c3.metric("Fatal Rate",        f"{fatal_pct:.2f}%")
    c4.metric("Serious Rate",      f"{serious_pct:.2f}%")

    st.divider()

    fig = make_subplots(
        rows=3, cols=3,
        subplot_titles=[
            "Accidents per Year", "Severity Distribution", "Gender Split",
            "By Month",           "By Day of Week",        "By Age Group",
            "Road Conditions",    "Speed Limit",           "Light Conditions",
        ],
        specs=[
            [{"type":"scatter"}, {"type":"domain"}, {"type":"bar"}],
            [{"type":"bar"},     {"type":"bar"},    {"type":"bar"}],
            [{"type":"bar"},     {"type":"bar"},    {"type":"domain"}],
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
    )

    yr = df.groupby("Year").size().reset_index(name="n")
    fig.add_trace(go.Scatter(x=yr["Year"], y=yr["n"], mode="lines+markers",
        line=dict(color="#1565C0", width=2), marker=dict(size=3), showlegend=False), row=1, col=1)

    sc = df["Severity"].value_counts()
    fig.add_trace(go.Pie(labels=sc.index, values=sc.values,
        marker_colors=[SEV_COLORS.get(s, "#999") for s in sc.index],
        textinfo="percent+label", showlegend=False, hole=0.3), row=1, col=2)

    gc = df["Gender"].value_counts()
    fig.add_trace(go.Bar(x=gc.index, y=gc.values,
        marker_color=[GEN_COLORS.get(g, "#999") for g in gc.index],
        showlegend=False), row=1, col=3)

    mo_vals = [df[df["Month"] == i].shape[0] for i in range(1, 13)]
    fig.add_trace(go.Bar(x=MONTH_ORDER, y=mo_vals, marker_color="#26A69A", showlegend=False), row=2, col=1)

    dv = [df[df["Day"] == d].shape[0] for d in DAY_ORDER]
    fig.add_trace(go.Bar(x=DAY_ORDER, y=dv, marker_color="#7E57C2", showlegend=False), row=2, col=2)

    ag = df["Age_Grp"].value_counts().reindex(AGE_ORDER).dropna()
    fig.add_trace(go.Bar(x=ag.index, y=ag.values, marker_color="#00897B", showlegend=False), row=2, col=3)

    rc = df["Road_conditions"].value_counts()
    fig.add_trace(go.Bar(x=rc.index, y=rc.values, marker_color="#F57C00", showlegend=False), row=3, col=1)

    sl = df.groupby("Speed_limit").size().reset_index(name="Count")
    fig.add_trace(go.Bar(x=sl["Speed_limit"].astype(str), y=sl["Count"],
        marker_color="#E53935", showlegend=False), row=3, col=2)

    lc = df["Light_conditions"].value_counts()
    fig.add_trace(go.Pie(labels=lc.index, values=lc.values,
        textinfo="percent+label", showlegend=False, hole=0.3), row=3, col=3)

    fig.update_layout(template="plotly_white", height=950, font=dict(size=10),
                      margin=dict(t=40))
    st.plotly_chart(fig, width="stretch")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 – TEMPORAL TRENDS
# ═════════════════════════════════════════════════════════════════════════════
with tab_temporal:
    st.subheader("Temporal Trends")

    yearly = df.groupby("Year").size().reset_index(name="Count")
    peak_yr = int(yearly.loc[yearly["Count"].idxmax(), "Year"]) if len(yearly) else 1983

    fig1 = px.line(yearly, x="Year", y="Count",
        title="<b>Annual Bicycle Accident Frequency</b>",
        markers=True, template="plotly_white",
        color_discrete_sequence=["#1565C0"],
        labels={"Count": "Number of Accidents"})
    fig1.update_traces(marker=dict(size=5))
    fig1.update_layout(yaxis=dict(tickformat=","), height=420,
        annotations=[dict(
            x=peak_yr,
            y=yearly.loc[yearly["Year"] == peak_yr, "Count"].values[0] if peak_yr in yearly["Year"].values else 0,
            text=f"Peak {peak_yr}", showarrow=True, arrowhead=2,
            ax=50, ay=-40, font=dict(color="red")
        )] if peak_yr in yearly["Year"].values else [])
    st.plotly_chart(fig1, width="stretch")

    fig2 = make_subplots(rows=1, cols=2,
        subplot_titles=("Accidents by Month", "Accidents by Day of Week"))
    mo_vals = [df[df["Month"] == i].shape[0] for i in range(1, 13)]
    fig2.add_trace(go.Bar(x=MONTH_ORDER, y=mo_vals, marker_color="#26A69A", showlegend=False), row=1, col=1)
    dv = [df[df["Day"] == d].shape[0] for d in DAY_ORDER]
    day_colors = ["#EF9A9A" if d in ("Saturday","Sunday") else "#7E57C2" for d in DAY_ORDER]
    fig2.add_trace(go.Bar(x=DAY_ORDER, y=dv, marker_color=day_colors, showlegend=False), row=1, col=2)
    fig2.update_layout(template="plotly_white", height=400,
        title_text="<b>Seasonal and Weekly Patterns</b>",
        yaxis=dict(tickformat=",", title="Accidents"),
        yaxis2=dict(tickformat=",", title="Accidents"))
    st.plotly_chart(fig2, width="stretch")

    hour_day = (
        df.dropna(subset=["Hour"])
          .groupby(["Day","Hour"])
          .size()
          .reset_index(name="Count")
    )
    pivot = (hour_day.pivot(index="Day", columns="Hour", values="Count")
                     .fillna(0)
                     .reindex(DAY_ORDER))
    fig3 = px.imshow(pivot,
        title="<b>Accident Frequency Heatmap: Hour of Day vs. Day of Week</b>",
        labels=dict(x="Hour of Day", y="Day of Week", color="Count"),
        color_continuous_scale="YlOrRd", template="plotly_white", aspect="auto")
    fig3.update_xaxes(dtick=1, tickmode="linear")
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, width="stretch")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 – SEVERITY
# ═════════════════════════════════════════════════════════════════════════════
with tab_severity:
    st.subheader("Severity Analysis")

    fig = make_subplots(rows=1, cols=2,
        subplot_titles=("Severity Distribution (All Time)", "Severity Trends Over Time"),
        specs=[[{"type":"domain"}, {"type":"scatter"}]])

    sc = df["Severity"].value_counts()
    fig.add_trace(go.Pie(labels=sc.index, values=sc.values,
        marker_colors=[SEV_COLORS.get(s,"#999") for s in sc.index],
        textinfo="percent+label+value", hole=0.35, showlegend=False), row=1, col=1)

    for sev in SEVERITY_ORDER:
        sev_yr = df[df["Severity"] == sev].groupby("Year").size().reset_index(name="Count")
        fig.add_trace(go.Scatter(x=sev_yr["Year"], y=sev_yr["Count"], name=sev,
            mode="lines", line=dict(color=SEV_COLORS[sev], width=2)), row=1, col=2)

    fig.update_layout(template="plotly_white", height=460,
        title_text="<b>Accident Severity Analysis</b>",
        yaxis2=dict(tickformat=",", title="Number of Accidents"),
        legend_title="Severity")
    st.plotly_chart(fig, width="stretch")

    hour_sev = (
        df.dropna(subset=["Hour"])
          .groupby(["Hour","Severity"])
          .size()
          .reset_index(name="Count")
    )
    fig_hs = px.bar(hour_sev, x="Hour", y="Count", color="Severity",
        color_discrete_map=SEV_COLORS,
        title="<b>Accidents by Hour of Day and Severity</b>",
        template="plotly_white", labels={"Count":"Accidents"}, barmode="stack")
    fig_hs.update_layout(height=400, yaxis=dict(tickformat=","), legend_title="Severity")
    st.plotly_chart(fig_hs, width="stretch")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 – DEMOGRAPHICS
# ═════════════════════════════════════════════════════════════════════════════
with tab_demo:
    st.subheader("Demographic Analysis")

    fig = make_subplots(rows=1, cols=2,
        subplot_titles=("Accidents by Gender", "Accidents by Age Group"))
    gc = df["Gender"].value_counts()
    fig.add_trace(go.Bar(x=gc.index, y=gc.values,
        marker_color=[GEN_COLORS.get(g,"#999") for g in gc.index],
        text=[f"{v:,}" for v in gc.values], textposition="outside", showlegend=False), row=1, col=1)
    ag = df["Age_Grp"].value_counts().reindex(AGE_ORDER).dropna()
    fig.add_trace(go.Bar(x=ag.index, y=ag.values, marker_color="#00897B",
        text=[f"{v:,}" for v in ag.values], textposition="outside", showlegend=False), row=1, col=2)
    fig.update_layout(template="plotly_white", height=440,
        title_text="<b>Cyclist Demographics</b>",
        yaxis=dict(tickformat=","), yaxis2=dict(tickformat=","))
    st.plotly_chart(fig, width="stretch")

    fig2 = make_subplots(rows=1, cols=2,
        subplot_titles=("Severity by Gender (grouped)", "Severity by Age Group (grouped)"))
    for sev in SEVERITY_ORDER:
        sub = df[df["Severity"] == sev].groupby("Gender").size().reset_index(name="Count")
        fig2.add_trace(go.Bar(name=sev, x=sub["Gender"], y=sub["Count"],
            marker_color=SEV_COLORS[sev]), row=1, col=1)
    for sev in SEVERITY_ORDER:
        sub = df[df["Severity"] == sev].groupby("Age_Grp").size().reset_index(name="Count")
        sub["Age_Grp"] = pd.Categorical(sub["Age_Grp"], categories=AGE_ORDER, ordered=True)
        sub = sub.sort_values("Age_Grp")
        fig2.add_trace(go.Bar(name=sev, x=sub["Age_Grp"], y=sub["Count"],
            marker_color=SEV_COLORS[sev], showlegend=False), row=1, col=2)
    fig2.update_layout(template="plotly_white", barmode="group", height=450,
        title_text="<b>Severity by Demographic Group</b>",
        yaxis=dict(tickformat=","), yaxis2=dict(tickformat=","),
        legend_title="Severity")
    st.plotly_chart(fig2, width="stretch")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 5 – ENVIRONMENT & ROADS
# ═════════════════════════════════════════════════════════════════════════════
with tab_env:
    st.subheader("Environmental Factors & Road Characteristics")

    fig = make_subplots(rows=1, cols=2,
        subplot_titles=("Road Surface Conditions", "Weather Conditions"))
    rc = df["Road_conditions"].value_counts()
    wc = df["Weather_conditions"].value_counts()
    fig.add_trace(go.Bar(x=rc.values, y=rc.index, orientation="h",
        marker_color="#F57C00", text=[f"{v:,}" for v in rc.values],
        textposition="outside", showlegend=False), row=1, col=1)
    fig.add_trace(go.Bar(x=wc.values, y=wc.index, orientation="h",
        marker_color="#1976D2", text=[f"{v:,}" for v in wc.values],
        textposition="outside", showlegend=False), row=1, col=2)
    fig.update_layout(template="plotly_white", height=440,
        title_text="<b>Environmental Conditions at Time of Accident</b>",
        xaxis=dict(tickformat=","), xaxis2=dict(tickformat=","))
    st.plotly_chart(fig, width="stretch")

    col_lc, col_rt = st.columns(2)
    with col_lc:
        lc = df["Light_conditions"].value_counts()
        fig_lc = px.pie(values=lc.values, names=lc.index,
            title="<b>Accidents by Light Conditions</b>",
            color_discrete_sequence=["#FFF176","#1565C0","#37474F"],
            template="plotly_white", hole=0.3)
        fig_lc.update_traces(textposition="inside", textinfo="percent+label+value")
        fig_lc.update_layout(height=420)
        st.plotly_chart(fig_lc, width="stretch")

    with col_rt:
        rt = df["Road_type"].value_counts()
        fig_rt = px.bar(x=rt.values, y=rt.index, orientation="h",
            title="<b>Accidents by Road Type</b>",
            labels={"x":"Accidents","y":"Road Type"},
            color=rt.values, color_continuous_scale="Greens",
            template="plotly_white")
        fig_rt.update_traces(showlegend=False)
        fig_rt.update_layout(height=420, coloraxis_showscale=False,
            xaxis=dict(tickformat=","))
        st.plotly_chart(fig_rt, width="stretch")

    sl = df.groupby("Speed_limit").size().reset_index(name="Count")
    fig_sl = px.bar(sl, x="Speed_limit", y="Count",
        title="<b>Accidents by Posted Speed Limit (mph)</b>",
        labels={"Speed_limit":"Speed Limit (mph)","Count":"Accidents"},
        color="Count", color_continuous_scale="Reds",
        template="plotly_white")
    fig_sl.update_layout(height=380, yaxis=dict(tickformat=","),
        coloraxis_showscale=False)
    st.plotly_chart(fig_sl, width="stretch")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 6 – RISK ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
with tab_risk:
    st.subheader("Risk Factor Analysis (Prescriptive Statistics)")
    st.info(
        "**Why rates matter:** Dry roads have the most accidents simply because most "
        "cycling happens in dry weather. The serious/fatal *rate* removes this volume "
        "bias and reveals which conditions are truly most dangerous."
    )

    def make_risk_table(group_col):
        t = (df.groupby(group_col)
               .agg(Accidents=("Is_Fatal","count"),
                    Fatal=("Is_Fatal","sum"),
                    Fatal_Rate=("Is_Fatal","mean"),
                    SF_Rate=("Is_SF","mean"))
               .reset_index())
        t["Fatal_%"] = (t["Fatal_Rate"] * 100).round(2)
        t["SF_%"]    = (t["SF_Rate"] * 100).round(2)
        return t.drop(columns=["Fatal_Rate","SF_Rate"]).sort_values("SF_%", ascending=False)

    road_risk = make_risk_table("Road_conditions").sort_values("SF_%")
    fig1 = px.bar(road_risk, x="SF_%", y="Road_conditions", orientation="h",
        title="<b>Serious or Fatal Rate by Road Surface Condition (%)</b>",
        text="SF_%", color="SF_%",
        color_continuous_scale="RdYlGn_r", template="plotly_white")
    fig1.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig1.update_layout(xaxis_title="Serious + Fatal Rate (%)",
        coloraxis_showscale=False, height=370)
    st.plotly_chart(fig1, width="stretch")

    speed_risk = (df.groupby("Speed_limit")
                    .agg(Total=("Is_Fatal","count"),
                         Fatal_Rate=("Is_Fatal","mean"),
                         SF_Rate=("Is_SF","mean"))
                    .reset_index())
    speed_risk["Fatal_%"] = (speed_risk["Fatal_Rate"] * 100).round(2)
    speed_risk["SF_%"]    = (speed_risk["SF_Rate"] * 100).round(2)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=speed_risk["Speed_limit"].astype(str), y=speed_risk["SF_%"],
        name="Serious + Fatal", marker_color="#FF9800"))
    fig2.add_trace(go.Bar(x=speed_risk["Speed_limit"].astype(str), y=speed_risk["Fatal_%"],
        name="Fatal Only", marker_color="#F44336"))
    fig2.update_layout(template="plotly_white", height=420,
        title="<b>Serious/Fatal Accident Rate by Posted Speed Limit (%)</b>",
        xaxis_title="Speed Limit (mph)", yaxis_title="Rate (%)",
        barmode="overlay", legend_title="Metric")
    st.plotly_chart(fig2, width="stretch")

    st.markdown("#### Detailed Risk Breakdown Tables")
    col1, col2 = st.columns(2)
    with col1:
        light_risk = make_risk_table("Light_conditions")
        st.markdown("**By Light Conditions**")
        st.dataframe(light_risk.set_index("Light_conditions"), use_container_width=True)

        road_risk2 = make_risk_table("Road_type")
        st.markdown("**By Road Type**")
        st.dataframe(road_risk2.set_index("Road_type"), use_container_width=True)

    with col2:
        weather_risk = make_risk_table("Weather_conditions")
        st.markdown("**By Weather Conditions**")
        st.dataframe(weather_risk.set_index("Weather_conditions"), use_container_width=True)

    st.divider()
    st.markdown("""
**Key Prescriptive Recommendations**

| Priority | Recommendation |
|----------|----------------|
| **High** | Enforce reduced speed limits near cycle routes; physical calming on 60–70 mph roads |
| **High** | Expand street lighting on routes with high nighttime cycling volumes |
| **Medium** | Launch winter cycling safety campaigns (ice, frost, fog awareness) before November |
| **Medium** | Target male commuter cyclists (ages 26–45) with safety messaging during peak hours |
| **Low** | Improve intersection design on single carriageways, which account for the majority of accidents by road type |
""")
