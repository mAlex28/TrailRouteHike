import streamlit as st
import pandas as pd
import json
import random
import pydeck as pdk
from src.query import answer_question

st.set_page_config(page_title="TrailRouteHike", layout="wide")

# Styles
st.markdown(
    """
    <style>
    :root {
        --primary-green: #79B473;
    }

    /* Buttons */
    .stButton > button {
        background-color: #79B473;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }

    .stButton > button:hover {
        background-color: #6AA866;
        color: white;
    }

    /* Title styling */
    h1 {
        color: #2f5d32;
    }

    /* Checkbox accent */
    input[type="checkbox"] {
        accent-color: #79B473;
    }

    /* Selectbox highlight */
    div[data-baseweb="select"] {
        border-color: #79B473;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ---- Header ----
h1, h2, h3 = st.columns([1,2,1])

with h2:
    st.markdown(
        """
        <h1 style='text-align: center;'>TrailStation</h1>
        <p style='text-align: center;'>Plan train-accessible hikes across the UK</p>
        """,
        unsafe_allow_html=True)

left, right = st.columns([1,1.5])

# ---- Main Layout ----

# Load dataset
with open("data/trails_with_stations.json") as f:
    trails = json.load(f)

df = pd.DataFrame(trails)

# ---- Left Layout ----
user_question = left.text_input("Where do you want to go?")

difficulty = left.selectbox("Choose difficulty", ["All", "Easy", "Medium", "Hard"])
short_hike = left.checkbox("Show only short hikes (<5 miles)")

col1, col2 = left.columns(2)
plan_btn = col1.button("Plan my hike")
surprise_btn = col2.button("Surprise me")

# Apply filters
filtered_df = df.copy()

if difficulty != "All":
    filtered_df = filtered_df[filtered_df["difficulty"].str.lower() == difficulty.lower()]

if short_hike:
    filtered_df = filtered_df[filtered_df["distance_km"] <= 8]

# ---- Right Layout ----
map_df = df[df["start_coord"].apply(lambda x: isinstance(x, list) and len(x) == 2)]

map_df = map_df.assign(
    lat=map_df["start_coord"].apply(lambda x: float(x[0])),
    lon=map_df["start_coord"].apply(lambda x: float(x[1]))
)

def difficulty_to_color(d):
    d = str(d).lower()
    if d == "easy":
        return [121, 180, 115]   # green
    elif d == "medium":
        return [255, 215, 0]     # yellow
    elif d == "hard":
        return [220, 20, 60]     # red
    else:
        return [0, 140, 255]     # default blue

map_df['difficulty_color'] = map_df['difficulty'].apply(difficulty_to_color)
map_df[['difficulty_color_r', 'difficulty_color_g', 'difficulty_color_b']] = pd.DataFrame(map_df['difficulty_color'].tolist(), index=map_df.index)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_df,
    get_position="[lon, lat]",
    get_radius=700, 
    get_fill_color="[difficulty_color_r, difficulty_color_g, difficulty_color_b]",
    pickable=True,
)

tooltip = {
    "html": """
    <b>{name}</b><br/>
    Difficulty: {difficulty}<br/>
    Distance: {distance_km} km<br/>
    Nearest station: {nearest_station}
    """,
    "style": {
        "backgroundColor": "white",
        "color": "black",
        "fontSize": "16px",
        "padding": "20px",
        "borderRadius": "6px"
    }
}

deck = pdk.Deck(
    layers=[layer],
    map_style=pdk.map_styles.ROAD,
    initial_view_state=pdk.ViewState(
        latitude=54.5,
        longitude=-2.5,
        zoom=8
    ),
    tooltip=tooltip
)

right.pydeck_chart(deck)

# 'Plan hike' button
if plan_btn:
    if not user_question.strip():
        left.warning("Please enter a location")
        st.stop()

    try:
        with left.spinner("Planning your hike..."):
            answer = answer_question(user_question)

        if answer:
            left.subheader("Suggested Itinerary")
            left.markdown(answer)
        else:
            raise ValueError("AI returned empty answer")

    except Exception:

        # FALLBACK → show matching trails insteads
        left.warning("Couldn't generate itinerary. Showing matching hikes instead.")

        if df.empty:
            left.info("No trails match your filters.")
        else:
            left.subheader("Matching Trails")
            left.dataframe(filtered_df[["name","difficulty","distance_km"]])


# 'Surprise me' button
if surprise_btn:
    if filtered_df.empty:
        left.info("No trails available with current filters.")
    else:
        trail = filtered_df.sample(1).iloc[0]

        left.subheader("🎲 Surprise Hike")
        left.write(f"**{trail['name']}**")
        left.write(f"Difficulty: {trail['difficulty']}")
        left.write(f"Distance: {trail['distance_km']} km")
        # left.write(f"Country: {trail['country']}")
        left.write(f"Nearest station: {trail['nearest_station']}")

        lat, lon = trail["start_coord"]
        map_df = pd.DataFrame({"lat":[lat], "lon":[lon]})
        right.map(map_df)

