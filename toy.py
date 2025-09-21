import streamlit as st
import pandas as pd
import random

import streamlit as st



# --- PAGE CONFIG & GLOBAL CSS ---
st.set_page_config(
    page_title="Family Fun Hub",
    page_icon="🎠",
    layout="wide"
)

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
    background-color: #FFFDF8;
    color: #333333;
}
h1, h2, h3 { color: #2E5984; font-weight: 700; }
div.stButton > button {
    background-color: #FFB347; color: white; border-radius: 8px; 
    border: none; padding: 0.6em 1.2em; font-size: 1em; font-weight: 600;
    transition: background-color 0.3s ease;
}
div.stButton > button:hover { background-color: #FF9F1C; }
section[data-testid="stSidebar"] { background-color: #FCEFEF; }
.card {
    background-color: white; border-radius: 12px; padding: 1em;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05); text-align: center;
    transition: transform 0.2s ease;
}
.card:hover { transform: translateY(-4px); }
</style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data


def load_toys():
    df = pd.read_csv("toys.csv")

    # Standardize all column names (strip spaces)
    df.columns = df.columns.str.strip()

    # Ensure ALL required columns exist
    required_cols = [
        "name", "age_range", "attention_span", "disabilities",
        "goals", "interests", "price", "play_type", "preferences",
        "url", "image_url"
    ]
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""  # fallback empty column

    # Safe age parsing
    df[["min_age", "max_age"]] = (
        df["age_range"]
        .fillna("0-18")
        .astype(str)
        .str.split("-", n=1, expand=True)
    )
    df["min_age"] = pd.to_numeric(df["min_age"], errors="coerce").fillna(0).astype(int)
    df["max_age"] = pd.to_numeric(df["max_age"], errors="coerce").fillna(18).astype(int)

    # Normalize list-like columns (disabilities, goals, interests, preferences)
    for col in ["disabilities", "goals", "interests", "preferences"]:
        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
            .apply(lambda s: [i.strip() for i in s.split(";") if i.strip()])
        )

    # Safe numeric price
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)

    return df


toys = load_toys()

# --- USER INPUT QUESTIONS ---
st.markdown("<h1 style='text-align:center;'>🎠 Find the Perfect Toy 🎠</h1>", unsafe_allow_html=True)
st.write("Answer 8 quick questions and get 5–15 tailored toy recommendations.")

col1, col2 = st.columns(2)
with col1:
    age = st.slider("1. How old is the child?", 0, 18, 5)
    attention_options = ["Under 5 minutes", "5–10 minutes", "10–20 minutes", "20+ minutes"]
    attention = st.selectbox("2. Attention span?", attention_options)
    disability_options = [
        "Colorblindness", "Hearing accessibility",
        "Mobility friendly", "Other"
    ]
    disabilities = st.multiselect(
        "3. Special disabilities (if any):", disability_options
    )
    goal_options = [
        "STEM",
        "Sensory and multisensory development",
        "Imaginative and creative thinking",
        "Motor skills and physical coordination",
        "Tech and electrical exploration",
        "Educational and cognitive growth"
    ]
    goal = st.selectbox("4. Goals for child:", goal_options)

with col2:
    interest_options = ["Animals", "Vehicles", "Fantasy", "Science", "Art & Crafts"]
    interests = st.multiselect(
        "5. Child's interests (pick one or more):", interest_options
    )
    budget = st.number_input(
        "6. Parent's budget (USD):", min_value=0.0, value=50.0, step=1.0
    )
    play_type = st.radio(
        "7. Play style?", ["Independently", "Socially with friends"]
    )
    preference_options = [
        "Travel safe", "Compact storage", "Low mess level",
        "Washable", "Indestructible", "No assembly required",
        "Culturally inclusive"
    ]
    preferences = st.multiselect(
        "8. Additional preferences:", preference_options
    )

find = st.button("🔍 Find Toys")



# --- FILTERING & RESULTS ---
if find:
    df = toys.copy()

    # Age filter
    df = df[(df["min_age"] <= age) & (df["max_age"] >= age)]

    # Attention filter
    if "attention_span" in df.columns:
        df = df[df["attention_span"] == attention]

    # Disabilities filter
    for d in disabilities:
        if "disabilities" in df.columns:
            df = df[df["disabilities"].apply(lambda L: d in L)]

    # Goal filter
    if "goals" in df.columns:
        df = df[df["goals"].apply(lambda L: goal in L)]

    # Interests filter
    if "interests" in df.columns and interests:
        df = df[df["interests"].apply(lambda L: any(i in L for i in interests))]

    # Price filter
    if "price" in df.columns:
        df = df[df["price"] <= budget]

    # Play type filter
    if "play_type" in df.columns:
        df = df[df["play_type"] == play_type]

    # Preferences filter
    for p in preferences:
        if "preferences" in df.columns:
            df = df[df["preferences"].apply(lambda L: p in L)]


    # Ensure at least 5 results by padding with best‐matches if needed
    if len(df) < 5:
        candidates = toys.loc[~toys.index.isin(df.index)].copy()
        def score(row):
            s = 0
            if row["min_age"] <= age <= row["max_age"]: s += 1
            if row["attention_span"] == attention: s += 1
            if goal in row["goals"]: s += 1
            s += sum(i in row["interests"] for i in interests)
            if row["price"] <= budget: s += 1
            if row["play_type"] == play_type: s += 1
            s += sum(p in row["preferences"] for p in preferences)
            return s
        candidates["score"] = candidates.apply(score, axis=1)
        extras = candidates.sort_values("score", ascending=False).head(5 - len(df))
        df = (
    pd.concat([df, extras], ignore_index=True)
      .drop_duplicates(subset="name", keep="first")
)
    # Cap at 15KeyError: 'interests'



    if len(df) > 15:
        df = df.sample(15, random_state=42)

    # Display cards
    st.markdown("### 🎁 Your Toy Matches:")
    cols = st.columns(3)
    for idx, toy in df.iterrows():
        col = cols[idx % 3]
        with col:
            st.markdown(f"""
                <div class="card">
                  <a href="{toy['url']}" target="_blank">
                    <img src="{toy['image_url']}" width="150">
                  </a>
                  <h4>{toy['name']}</h4>
                  <p>${toy['price']:.2f}</p>
                </div>
            """, unsafe_allow_html=True)

    if df.empty:
        st.warning("No matching toys found. Try loosening some filters.")

# --- FOOTER ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:gray;'>"
    "© 2025 Family Fun Hub | Crafted with ❤️ for families"
    "</p>",
    unsafe_allow_html=True
)