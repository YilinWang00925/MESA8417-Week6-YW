import streamlit as st
import pandas as pd
import altair as alt
import os

st.title("Albany Airbnb Listings Analysis: Price, Review Scores and Accommodates")

DATA_PATH = "uploaded_data.csv"

# --- Silent file loading ---
if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
else:
    df = None
    st.warning("No dataset found. Please upload 'uploaded_data.csv' to the app folder.")

if df is not None:
    # 1. Distribution of price with dropdown for accommodates
    st.subheader("Distribution of Price by Accommodates")
    if 'accommodates' in df.columns:
        accommodates_options = sorted(df['accommodates'].dropna().unique())
        selected_accommodates = st.selectbox("Select accommodates", accommodates_options)
        filtered_df = df[df['accommodates'] == selected_accommodates]
    else:
        st.warning("No 'accommodates' column found.")
        filtered_df = df

    price_dist_chart = alt.Chart(filtered_df).mark_bar().encode(
        x=alt.X('price:Q', bin=alt.Bin(maxbins=30), title='Price'),
        y=alt.Y('count()', title='Number of Listings'),
        tooltip=['count()']
    ).properties(
        width=400,
        height=300
    )
    st.altair_chart(price_dist_chart, use_container_width=True)

    # 2. Accommodates Bar chart + Scatter plot with linked selection
    st.subheader("Price vs Review Score by Accommodates")

    if 'accommodates' in df.columns:
        acc_select = alt.selection_single(fields=['accommodates'], empty='all', name="AccommodatesBar")

        # Bar chart
        accommodates_bar = alt.Chart(df).mark_bar().encode(
            x=alt.X('accommodates:O', title='Accommodates'),
            y=alt.Y('count()', title='Number of Listings'),
            color=alt.condition(acc_select, alt.value('orange'), alt.value('lightgray')),
            tooltip=['accommodates', 'count()']
        ).add_params(
            acc_select
        ).properties(
            width=400,
            height=200
        )

        # Determine review column
        review_col = "review_scores_rating" if "review_scores_rating" in df.columns else df.columns[-1]
        if "review_scores_rating" not in df.columns:
            st.warning("No review score column found with the name 'review_scores_rating'. Using last column instead.")

        # Scatter plot
        scatter = alt.Chart(df).mark_circle(size=60, opacity=0.7).encode(
            x=alt.X('price:Q', title='Price'),
            y=alt.Y(
                f'{review_col}:Q',
                title='Review Score',
                scale=alt.Scale(domain=[0, 5]),
                axis=alt.Axis(tickMinStep=0.5)
            ),
            color=alt.condition(
                acc_select,
                alt.value('orange'),
                alt.value('lightgray')
            ),
            tooltip=['room_type', 'price', review_col, 'accommodates'] if 'room_type' in df.columns else ['price', review_col, 'accommodates']
        ).add_params(
            acc_select
        ).properties(
            width=400,
            height=300
        )

        # Combine the two charts vertically so selection syncs
        combined_chart = (accommodates_bar & scatter).resolve_scale(
            color='independent'
        )
        st.altair_chart(combined_chart, use_container_width=True)
    else:
        st.warning("No 'accommodates' column found.")
