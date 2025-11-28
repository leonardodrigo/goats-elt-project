import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(
    page_title="California Housing EDA",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent.parent / "data" / "california_housing.csv"


@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        st.error(
            f"Data file not found at: {DATA_PATH}\n\n"
            "Run `uv run python src/export_california_data.py` locally to create it, "
            "then commit the CSV so it is shipped in the Docker image."
        )
        st.stop()

    df = pd.read_csv(DATA_PATH)

    df = df.rename(
        columns={
            "MedInc": "Median_Income",
            "HouseAge": "House_Age",
            "AveRooms": "Avg_Rooms",
            "AveBedrms": "Avg_Bedrooms",
            "Population": "Population",
            "AveOccup": "Avg_Occupancy",
            "Latitude": "Latitude",
            "Longitude": "Longitude",
            "MedHouseVal": "Median_House_Value",
        }
    )

    df["Region"] = pd.cut(
        df["Latitude"],
        bins=[df["Latitude"].min() - 0.01, 34, 37, df["Latitude"].max() + 0.01],
        labels=["South", "Central", "North"],
    )

    df["Coastal"] = pd.cut(
        df["Longitude"],
        bins=[df["Longitude"].min() - 0.01, -120, df["Longitude"].max() + 0.01],
        labels=["Inland", "Coastal"],
    )

    return df


df = load_data()

numeric_cols = df.select_dtypes(include="number").columns.tolist()
categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

st.title("California Housing Dataset — EDA Dashboard")

st.sidebar.header("Filters")


def slider_filter(df, col):
    m1, m2 = float(df[col].min()), float(df[col].max())
    return st.sidebar.slider(
        col.replace("_", " "),
        min_value=m1,
        max_value=m2,
        value=(m1, m2),
    )


filters = {col: slider_filter(df, col) for col in numeric_cols}

filtered_df = df.copy()
for col, (low, high) in filters.items():
    filtered_df = filtered_df[(filtered_df[col] >= low) & (filtered_df[col] <= high)]

st.sidebar.markdown(f"### Rows after filtering: **{len(filtered_df)}**")

if filtered_df.empty:
    st.warning("No data left after filtering.")
    st.stop()

tab_overview, tab_dist, tab_rel, tab_groups, tab_map = st.tabs(
    ["Overview", "Distributions", "Relationships", "Groups", "Map"]
)

with tab_overview:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Median House Value (mean)",
        f"${filtered_df['Median_House_Value'].mean():,.2f}",
    )
    col2.metric("Median Income (mean)", f"{filtered_df['Median_Income'].mean():.2f}")
    col3.metric("Avg House Age", f"{filtered_df['House_Age'].mean():.1f}")
    col4.metric("Avg Population", f"{filtered_df['Population'].mean():,.0f}")
    st.dataframe(filtered_df.head(20), use_container_width=True)

with tab_dist:
    dist_col = st.selectbox(
        "Numeric column:",
        numeric_cols,
        index=numeric_cols.index("Median_House_Value"),
    )

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.histplot(filtered_df[dist_col], kde=True, ax=ax)
    st.pyplot(fig)

with tab_rel:
    x_col = st.selectbox(
        "X-axis",
        numeric_cols,
        index=numeric_cols.index("Median_Income"),
    )
    y_col = st.selectbox(
        "Y-axis",
        numeric_cols,
        index=numeric_cols.index("Median_House_Value"),
    )

    hue_options = [None] + categorical_cols
    hue_col = st.selectbox("Color by", hue_options)

    cols = [x_col, y_col] + ([hue_col] if hue_col else [])
    rel_df = filtered_df[cols].dropna()

    if len(rel_df) > 5000:
        rel_df = rel_df.sample(5000, random_state=42)

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    args = {"data": rel_df, "x": x_col, "y": y_col, "ax": ax2}

    if hue_col:
        args["hue"] = hue_col
        args["palette"] = "viridis"

    sns.scatterplot(**args)
    st.pyplot(fig2)

    corr_cols = st.multiselect(
        "Correlation columns",
        numeric_cols,
        default=[
            "Median_House_Value",
            "Median_Income",
            "House_Age",
            "Avg_Rooms",
            "Avg_Bedrooms",
        ],
    )

    if len(corr_cols) >= 2:
        fig3, ax3 = plt.subplots(figsize=(8, 6))
        sns.heatmap(
            filtered_df[corr_cols].corr(),
            cmap="coolwarm",
            annot=True,
            fmt=".2f",
            ax=ax3,
        )
        st.pyplot(fig3)

with tab_groups:
    gcol = st.selectbox(
        "Group by",
        [c for c in categorical_cols if c in ["Region", "Coastal"]] or categorical_cols,
    )
    tcol = st.selectbox(
        "Target",
        numeric_cols,
        index=numeric_cols.index("Median_House_Value"),
    )

    stats = filtered_df.groupby(gcol, observed=True)[tcol].mean().sort_values()

    fig4, ax4 = plt.subplots(figsize=(8, 4))
    stats.plot(kind="barh", ax=ax4)
    st.pyplot(fig4)

    tg = filtered_df[gcol].value_counts().head(8).index
    box_df = filtered_df[filtered_df[gcol].isin(tg)]

    fig5, ax5 = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=box_df, x=gcol, y=tcol, ax=ax5)
    st.pyplot(fig5)

with tab_map:
    map_df = filtered_df.rename(columns={"Latitude": "lat", "Longitude": "lon"})[
        ["lat", "lon"]
    ].dropna()

    if len(map_df) > 1000:
        map_df = map_df.sample(1000, random_state=42)

    st.map(map_df)
