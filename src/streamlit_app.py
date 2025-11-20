import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_california_housing

st.set_page_config(
    page_title="California Housing EDA",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    data = fetch_california_housing(as_frame=True)
    df = data.frame.rename(columns={
        "MedInc": "Median_Income",
        "HouseAge": "House_Age",
        "AveRooms": "Avg_Rooms",
        "AveBedrms": "Avg_Bedrooms",
        "Population": "Population",
        "AveOccup": "Avg_Occupancy",
        "Latitude": "Latitude",
        "Longitude": "Longitude",
        "MedHouseVal": "Median_House_Value"
    })

    # Simple region labels so we can do grouped plots (Idea for Spotify: genres)
    df["Region"] = pd.cut(
        df["Latitude"],
        bins=[df["Latitude"].min() - 0.01, 34, 37, df["Latitude"].max() + 0.01],
        labels=["South", "Central", "North"]
    )
    df["Coastal"] = pd.cut(
        df["Longitude"],
        bins=[df["Longitude"].min() - 0.01, -120, df["Longitude"].max() + 0.01],
        labels=["Inland", "Coastal"]
    )
    return df

df = load_data()
numeric_cols = df.select_dtypes(include="number").columns.tolist()
categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

st.title("California Housing Dataset — EDA Dashboard")
st.markdown("Explore the California Housing dataset using filters and interactive visualizations.")

# Sidebar filters
st.sidebar.header("Filters")

def slider_filter(df, col):
    min_val, max_val = float(df[col].min()), float(df[col].max())
    return st.sidebar.slider(col.replace("_", " "), min_val, max_val, (min_val, max_val))

filters = {}
for col in numeric_cols:
    filters[col] = slider_filter(df, col)

filtered_df = df.copy()
for col, (low, high) in filters.items():
    filtered_df = filtered_df[(filtered_df[col] >= low) & (filtered_df[col] <= high)]

st.sidebar.markdown(f"### Rows after filtering: **{len(filtered_df)}**")

if filtered_df.empty:
    st.warning("No data left after filtering — relax your filters in the sidebar.")
    st.stop()

# Tabs
tab_overview, tab_dist, tab_rel, tab_groups, tab_map = st.tabs(
    ["Overview", "Distributions", "Relationships", "Groups", "Map"]
)

# Overview
with tab_overview:
    st.subheader("Summary Metrics")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Median House Value (mean)", f"${filtered_df['Median_House_Value'].mean():,.2f}")
    col2.metric("Median Income (mean)", f"{filtered_df['Median_Income'].mean():.2f}")
    col3.metric("Avg House Age", f"{filtered_df['House_Age'].mean():.1f}")
    col4.metric("Avg Population", f"{filtered_df['Population'].mean():,.0f}")

    st.subheader("Dataset Preview")
    st.dataframe(filtered_df.head(20), use_container_width=True)

# Distributions
with tab_dist:
    st.subheader("Distribution of Numeric Features")

    dist_col = st.selectbox("Select a numeric column:", numeric_cols, index=numeric_cols.index("Median_House_Value") if "Median_House_Value" in numeric_cols else 0)

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.histplot(filtered_df[dist_col], kde=True, ax=ax)
    ax.set_xlabel(dist_col.replace("_", " "))
    st.pyplot(fig)

#  Relationships
with tab_rel:
    st.subheader("Scatter Plot Explorer")

    x_col = st.selectbox("X-axis", numeric_cols, index=numeric_cols.index("Median_Income") if "Median_Income" in numeric_cols else 0)
    y_col = st.selectbox("Y-axis", numeric_cols, index=numeric_cols.index("Median_House_Value") if "Median_House_Value" in numeric_cols else 1)
    hue_options = [None] + categorical_cols
    hue_col = st.selectbox("Color by (optional)", hue_options)

    rel_df = filtered_df[[x_col, y_col] + ([hue_col] if hue_col else [])].dropna()
    if len(rel_df) > 5000:
        rel_df = rel_df.sample(5000, random_state=42)

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    sns.scatterplot(
        data=rel_df,
        x=x_col,
        y=y_col,
        hue=hue_col if hue_col else None,
        palette="viridis",
        ax=ax2
    )
    ax2.set_xlabel(x_col.replace("_", " "))
    ax2.set_ylabel(y_col.replace("_", " "))
    st.pyplot(fig2)

    st.subheader("Correlation Heatmap")
    corr_cols = st.multiselect(
        "Select numeric columns for correlation:",
        numeric_cols,
        default=[c for c in numeric_cols if c in ["Median_House_Value", "Median_Income", "House_Age", "Avg_Rooms", "Avg_Bedrooms"]] or numeric_cols[:6],
    )

    if len(corr_cols) >= 2:
        fig3, ax3 = plt.subplots(figsize=(8, 6))
        sns.heatmap(filtered_df[corr_cols].corr(), cmap="coolwarm", annot=True, fmt=".2f", ax=ax3)
        st.pyplot(fig3)
    else:
        st.info("Select at least two numeric columns to see correlations.")

# Groups
with tab_groups:
    st.subheader("Grouped Analysis (Categories)")

    # Group by Stats, also useful for spotify later
    group_col = st.selectbox(
        "Group by (categorical):",
        [c for c in categorical_cols if c in ["Region", "Coastal"]] or categorical_cols
    )
    target_col = st.selectbox(
        "Target numeric column:",
        numeric_cols,
        index=numeric_cols.index("Median_House_Value") if "Median_House_Value" in numeric_cols else 0,
    )

    group_stats = (
        filtered_df.groupby(group_col)[target_col]
        .mean()
        .sort_values()
    )

    st.markdown("**Mean target per group**")
    fig4, ax4 = plt.subplots(figsize=(8, 4))
    group_stats.plot(kind="barh", ax=ax4)
    ax4.set_xlabel(f"Mean {target_col.replace('_', ' ')}")
    ax4.set_ylabel(group_col)
    st.pyplot(fig4)

    st.markdown("**Distribution per group (boxplot)**")
    top_groups = (
        filtered_df[group_col].value_counts().head(8).index
    )
    box_df = filtered_df[filtered_df[group_col].isin(top_groups)]

    fig5, ax5 = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=box_df, x=group_col, y=target_col, ax=ax5)
    ax5.set_xlabel(group_col)
    ax5.set_ylabel(target_col.replace("_", " "))
    ax5.tick_params(axis="x", rotation=45)
    st.pyplot(fig5)

# Map
with tab_map:
    st.subheader("Geographic Map of Houses")
    map_df = filtered_df.rename(columns={"Latitude": "lat", "Longitude": "lon"})
    sample_df = map_df[["lat", "lon"]].dropna()
    if len(sample_df) > 1000:
        sample_df = sample_df.sample(1000, random_state=42)
    st.map(sample_df)
