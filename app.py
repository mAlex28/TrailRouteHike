import streamlit as st
import pandas as pd
from src.query import answer_question
import json

st.set_page_config(
    page_title="TrailRouteHike",
    layout="wide"
)

st.title("TrailStation - AI Hiking Planner")
st.markdown("Plan hikes accessible by train, filtered by difficulty and distance.")

# User input
user_question = st.text_input("Where do you want to go?")

# Filters
difficulty = st.selectbox("Choose difficulty", ["All", "Easy", "Medium", "Hard"])
short_hike = st.checkbox("Show only short hikes (<5 miles)")

# Plan the hike
if st.button("Plan my hike"):
    if not user_question.strip():
        st.warning("Please enter a location or a question")
    else:
        with st.spinner("Finding the best trails..."):
            answer = answer_question(user_question)

        st.subheader("Suggested Itinerary")
        st.markdown(answer)

        # Map display
        try:
            with open("data/trails_with_stations.json") as f:
                trails = json.load(f)
            
            df = pd.DataFrame(trails)

            # Apply difficulty filter
            if difficulty != "All":
                df = df[df["difficulty"].str.lower() == difficulty.lower()]

            if short_hike:
                df = df[df["distance_km"] <= 8]

            if not df.empty:
                st.subheader("Map of Trails")
                st.map(df.assign(
                    lat=df["start_coord"].apply(lambda x: x[0]),
                    lon=df["start_coord"].apply(lambda x: x[1])
                )[["lat", "lon"]])
            else:
                st.info("No trails match your filters")
        except Exception as e:
            st.error("Failed to load map: {e}")