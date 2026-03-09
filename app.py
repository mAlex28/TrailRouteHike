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

# Sidebar
st.sidebar.header("Filters")
difficulty = st.sidebar.selectbox(
    "Choose difficulty",
    ["All", "Easy", "Medium", "Hard"]
)

short_hike = st.sidebar.checkbox("Show only short hikes (<6 miles)")

# User input
question = st.text_input("Where do you want to go?")

if st.button("Plan my hike"):
    result = answer_question(question)
    st.write(result)