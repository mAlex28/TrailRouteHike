import streamlit as st
import pandas as pd
import json
import pydeck as pdk
from src.query import answer_question

st.set_page_config(page_title="TrackAndTrail", layout="wide")

# ---- Styles ----
st.markdown(
    """
    <style>
    :root {
        --primary-green: #79B473;
    }
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
    h1 { color: #2f5d32; }
    input[type="checkbox"] { accent-color: #79B473; }
    div[data-baseweb="select"] { border-color: #79B473; }
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
        unsafe_allow_html=True
    )

left, right = st.columns([1,1.5])

# ---- Load dataset ----
with open("data/trails_with_stations.json") as f:
    trails = json.load(f)
df = pd.DataFrame(trails)

if "selected_trail" not in st.session_state:
    st.session_state.selected_trail = None

# ---- User input ----
user_question = left.text_input("Where do you want to go?")
difficulty = left.selectbox("Choose difficulty", ["All", "Easy", "Moderate", "Hard"])
short_hike = left.checkbox("Show only short hikes (<5 miles)")

col1, col2 = left.columns(2)
plan_btn = col1.button("Plan my hike")
surprise_btn = col2.button("Surprise me")

# ---- Filters ----
filtered_df = df.copy()
if difficulty != "All":
    filtered_df = filtered_df[filtered_df["difficulty"].str.lower() == difficulty.lower()]
if short_hike:
    filtered_df = filtered_df[filtered_df["distance_km"] <= 8.047]

# ---- Difficulty colors ----
def difficulty_to_color(d):
    d = str(d).lower()
    if d == "easy": return [121,180,115]    # green
    elif d in ["moderate", "medium"]: return [0,140,255]  # yellow
    elif d == "hard": return [220,20,60]    # red
    else: return [0,0,0]                     # black

df = df[df["start_coord"].apply(lambda x: isinstance(x, list) and len(x) == 2)]
df['difficulty_color'] = df['difficulty'].apply(difficulty_to_color)
df[['difficulty_color_r','difficulty_color_g','difficulty_color_b']] = pd.DataFrame(df['difficulty_color'].tolist(), index=df.index)

tooltip = {
    "html": """
    <b>{name}</b><br/>
    Difficulty: {difficulty}<br/>
    Distance: {distance_km} km<br/>
    Nearest station: {nearest_station}
    """,
    "style": {"backgroundColor": "white","color": "black","fontSize": "16px","padding": "20px","borderRadius": "6px"}
}

# ---- Map rendering ----
def render_map(selected_trail=None):
    layers = []

    all_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[start_coord[1], start_coord[0]]",
        get_radius=900,
        get_fill_color="[difficulty_color_r, difficulty_color_g, difficulty_color_b]",
        pickable=True,
        opacity=0.5 if selected_trail is not None else 1
    )
    layers.append(all_layer)

    if selected_trail is not None:
        highlight_df = pd.DataFrame([selected_trail])
        highlight_df['difficulty_color'] = highlight_df['difficulty'].apply(difficulty_to_color)
        highlight_df[['difficulty_color_r','difficulty_color_g','difficulty_color_b']] = pd.DataFrame(highlight_df['difficulty_color'].tolist(), index=highlight_df.index)

        hl_layer = pdk.Layer(
            "ScatterplotLayer",
            data=highlight_df,
            get_position="[start_coord[1], start_coord[0]]",
            get_radius=1500,
            get_fill_color="[difficulty_color_r, difficulty_color_g, difficulty_color_b]",
            pickable=True
        )
        layers.append(hl_layer)

        view = pdk.ViewState(
            latitude=float(selected_trail['start_coord'][0]),
            longitude=float(selected_trail['start_coord'][1]),
            zoom=9
        )
    else:
        view = pdk.ViewState(latitude=51.5, longitude=-0.12, zoom=7)

    deck = pdk.Deck(layers=layers, map_style=pdk.map_styles.ROAD, initial_view_state=view, tooltip=tooltip)
    right.pydeck_chart(deck, use_container_width=True)

# ---- Closest difficulty ----
difficulty_order = ["easy", "moderate", "hard"]

def find_closest_difficulty(df_area, requested):
    requested = requested.lower()
    if requested not in difficulty_order:
        return None
    req_index = difficulty_order.index(requested)
    df_area = df_area.copy()
    df_area["diff_distance"] = df_area["difficulty"].str.lower().apply(lambda x: abs(difficulty_order.index(x) - req_index))
    return df_area.sort_values("diff_distance").iloc[0]

if plan_btn:
    if not user_question.strip():
        left.warning("Please enter a location")
        st.stop()

    try:
        with left.spinner("Planning your hike..."):
            answer, selected = answer_question(user_question)
            
            warning_message = None

            # Check difficulty filter
            if difficulty != "All" and selected["difficulty"].lower() != difficulty.lower():
                
                # Search by country OR station name — not trail name
                area_trails = df[
                    df["country"].str.lower().str.contains(user_question.strip().lower(), na=False) |
                    df["nearest_station"].str.lower().str.contains(user_question.strip().lower(), na=False)
                ]

                if not area_trails.empty:
                    # Try to find exact difficulty match first
                    exact_match = area_trails[
                        area_trails["difficulty"].str.lower() == difficulty.lower()
                    ]
                    if not exact_match.empty:
                        selected = exact_match.iloc[0]
                    else:
                        # Fall back to closest difficulty
                        selected = find_closest_difficulty(area_trails, difficulty)
                        warning_message = (
                            f"No {difficulty} hikes found near {user_question}. "
                            f"Showing a {selected['difficulty']} hike instead."
                        )
                else:
                    # Search entire dataset for requested difficulty
                    any_difficulty = df[df["difficulty"].str.lower() == difficulty.lower()]
                    if not any_difficulty.empty:
                        selected = any_difficulty.iloc[0]
                        warning_message = (
                            f"No hikes found near {user_question}. "
                            f"Showing a {difficulty} hike from elsewhere instead."
                        )
                    else:
                        selected = None
                        warning_message = None

            # Check short hike filter (5 miles = 8.047 km)
            SHORT_HIKE_KM = 8.047
            if short_hike and selected is not None and selected["distance_km"] > SHORT_HIKE_KM:

                location_trails = df[
                    df["country"].str.lower().str.contains(user_question.strip().lower(), na=False) |
                    df["nearest_station"].str.lower().str.contains(user_question.strip().lower(), na=False)
                ]
                short_nearby = location_trails[location_trails["distance_km"] <= SHORT_HIKE_KM]

                if not short_nearby.empty:
                    selected = short_nearby.iloc[0]
                else:
                    any_short = df[df["distance_km"] <= SHORT_HIKE_KM]
                    if not any_short.empty:
                        selected = any_short.iloc[0]
                        warning_message = (
                            f"No short hikes (<5 miles) found near {user_question}. "
                            f"Showing another short hike instead."
                        )
                    else:
                        left.info("No short hikes (<5 miles) available.")
                        selected = None

        # ---- Display results AFTER spinner closes ----
        if selected is not None:
            if warning_message:
                left.warning(warning_message)

            left.subheader("Suggested Itinerary")
            display_answer = (
                f"**Recommended trail:** {selected['name']}  \n"
                f"**Location:** {selected.get('country', 'N/A')}  \n"
                f"**Difficulty:** {selected['difficulty']}  \n"
                f"**Distance:** {selected['distance_km']} km "
                f"({round(selected['distance_km'] / 1.609, 1)} miles)  \n"
                f"**Train station:** {selected['nearest_station']}  \n\n"
                f"{selected.get('description', '')}"
            )
            left.markdown(display_answer)
            st.session_state.selected_trail = selected
        else:
            left.info(f"No {difficulty.lower()} hikes found near {user_question}.")

    except Exception as e:
        left.warning(f"Couldn't generate itinerary: {e}")

        if not filtered_df.empty:
            left.subheader("Matching Trails")
            for _, row in filtered_df.iterrows():
                left.write(f"**{row['name']}** — {row['difficulty']} — {row['distance_km']} km")
            st.session_state.selected_trail = filtered_df.iloc[0]
        else:
            left.info("No trails match your filters.")
            st.session_state.selected_trail = None

# ---- Surprise me button ----
if surprise_btn:
    if filtered_df.empty:
        left.info("No trails available with current filters.")
    else:
        trail = filtered_df.sample(1).iloc[0]
        left.subheader("🎲 Surprise Hike")
        left.write(f"**{trail['name']}**")
        left.write(f"Difficulty: {trail['difficulty']}")
        left.write(f"Distance: {trail['distance_km']} km")
        left.write(f"Country: {trail['country']}")
        left.write(f"Nearest station: {trail['nearest_station']}")
        st.session_state.selected_trail = trail

# ---- Render map ----
render_map(st.session_state.selected_trail)