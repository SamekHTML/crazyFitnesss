"""
FitTrack X — A really cool gamified fitness & macro tracker.
Dark glassmorphic UI, animated progress rings, XP/levels, streaks, badges.

Built for: Python Workshop Final Project
Libraries: Streamlit, Pandas, Plotly
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import os
import base64
from PIL import Image

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

ASSETS_DIR = "assets"
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
BG_PATH = os.path.join(ASSETS_DIR, "background.jpg")

# Favicon: use the logo if it exists, otherwise fall back to an emoji
_page_icon = Image.open(LOGO_PATH) if os.path.exists(LOGO_PATH) else "⚡"

st.set_page_config(
    page_title="CrazyFitness",
    page_icon=_page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
WORKOUTS_FILE = os.path.join(DATA_DIR, "workouts.csv")
NUTRITION_FILE = os.path.join(DATA_DIR, "nutrition.csv")
DAILY_FILE = os.path.join(DATA_DIR, "daily_log.csv")
PROFILE_FILE = os.path.join(DATA_DIR, "profile.csv")


@st.cache_data
def get_base64(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


BG_B64 = get_base64(BG_PATH)
LOGO_B64 = get_base64(LOGO_PATH)

XP_PER_LEVEL = 300

MET_VALUES = {
    "Running (fast)": 11.5, "Running (moderate)": 8.3, "Jogging": 7.0,
    "Walking": 3.5, "Cycling (moderate)": 7.5, "Cycling (intense)": 10.0,
    "Weightlifting (general)": 5.0, "Weightlifting (heavy/vigorous)": 6.0,
    "HIIT": 8.0, "Yoga": 2.5, "Swimming": 8.0, "Basketball": 6.5,
    "Football/Soccer": 7.0, "Boxing": 9.0, "Rowing": 7.0,
    "Stretching/Mobility": 2.3, "Other": 5.0,
}

QUICK_FOODS = {
    "-- Select a quick-add food --": None,
    "Chicken Breast (100g)": {"cal": 165, "protein": 31, "carbs": 0, "fat": 3.6},
    "Rice, cooked (1 cup)": {"cal": 206, "protein": 4.3, "carbs": 45, "fat": 0.4},
    "Egg (1 large)": {"cal": 78, "protein": 6, "carbs": 0.6, "fat": 5},
    "Banana (1 medium)": {"cal": 105, "protein": 1.3, "carbs": 27, "fat": 0.4},
    "Whey Protein (1 scoop)": {"cal": 120, "protein": 24, "carbs": 3, "fat": 1},
    "Oats (1 cup dry)": {"cal": 307, "protein": 11, "carbs": 55, "fat": 5},
    "Peanut Butter (1 tbsp)": {"cal": 94, "protein": 4, "carbs": 3, "fat": 8},
    "Greek Yogurt (170g)": {"cal": 100, "protein": 17, "carbs": 6, "fat": 0.7},
    "Salmon (100g)": {"cal": 208, "protein": 20, "carbs": 0, "fat": 13},
    "Whole Wheat Bread (1 slice)": {"cal": 81, "protein": 4, "carbs": 14, "fat": 1.1},
}

QUOTES = [
    "Discipline is choosing between what you want now and what you want most.",
    "The pain of discipline weighs ounces; the pain of regret weighs tons.",
    "Small daily wins compound into unrecognizable results.",
    "Your body can stand almost anything. It's your mind you have to convince.",
    "Progress, not perfection.",
    "Sweat is just fat crying.",
    "You don't have to be extreme, just consistent.",
    "The only bad workout is the one that didn't happen.",
    "Levels don't come from comfort zones.",
    "Show up. That's most of the battle.",
]

BADGES = [
    {"id": "first_workout", "name": "First Steps", "emoji": "🏆",
     "desc": "Log your first workout", "cond": lambda s: s["total_workouts"] >= 1},
    {"id": "workout_10", "name": "Iron Regular", "emoji": "🏋️",
     "desc": "Log 10 workouts", "cond": lambda s: s["total_workouts"] >= 10},
    {"id": "workout_50", "name": "Gym Rat", "emoji": "💪",
     "desc": "Log 50 workouts", "cond": lambda s: s["total_workouts"] >= 50},
    {"id": "streak_3", "name": "Warming Up", "emoji": "🔥",
     "desc": "Reach a 3-day streak", "cond": lambda s: s["streak"] >= 3},
    {"id": "streak_7", "name": "Week Warrior", "emoji": "⚡",
     "desc": "Reach a 7-day streak", "cond": lambda s: s["streak"] >= 7},
    {"id": "streak_30", "name": "Unstoppable", "emoji": "🚀",
     "desc": "Reach a 30-day streak", "cond": lambda s: s["streak"] >= 30},
    {"id": "hydration_5", "name": "Hydration Hero", "emoji": "💧",
     "desc": "Hit your water goal 5 days", "cond": lambda s: s["water_goal_days"] >= 5},
    {"id": "steps_5", "name": "Steps Master", "emoji": "👣",
     "desc": "Hit your step goal 5 days", "cond": lambda s: s["steps_goal_days"] >= 5},
    {"id": "food_20", "name": "Macro Tracker", "emoji": "🍎",
     "desc": "Log 20 meals", "cond": lambda s: s["total_food_logs"] >= 20},
    {"id": "level_5", "name": "Level 5 Legend", "emoji": "🌟",
     "desc": "Reach Level 5", "cond": lambda s: s["level"] >= 5},
]

# ----------------------------------------------------------------------------
# THEME — dark glassmorphic CSS
# ----------------------------------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3, .grad-title { font-family: 'Space Grotesk', sans-serif; }

.stApp {
    background: radial-gradient(circle at 15% 0%, #1b1035 0%, #0a0a18 45%, #06060f 100%);
    color: #EDEDFB;
}
""" + (f"""
.stApp {{
    background-image:
        radial-gradient(circle at 15% 0%, rgba(27,16,53,0.88) 0%, rgba(10,10,24,0.93) 45%, rgba(6,6,15,0.96) 100%),
        url("data:image/jpeg;base64,{BG_B64}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
""" if BG_B64 else "") + """
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #120a24 0%, #0a0a18 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
#MainMenu, footer {visibility: hidden;}

.grad-title {
    font-size: 2.6rem; font-weight: 700; margin-bottom: 0;
    background: linear-gradient(90deg, #00F5D4, #9B5DE5 45%, #F15BB5 90%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.subtle { color: #9A93B8; font-size: 0.95rem; }

.glass-card {
    background: rgba(255,255,255,0.045);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.glass-card:hover { transform: translateY(-3px); box-shadow: 0 14px 36px rgba(0,0,0,0.45); }

.stat-icon { font-size: 1.5rem; }
.stat-value { font-size: 1.7rem; font-weight: 700; color: #fff; margin: 2px 0; }
.stat-label { font-size: 0.8rem; color: #9A93B8; text-transform: uppercase; letter-spacing: 0.06em; }
.stat-sub { font-size: 0.78rem; color: #6FE7C7; }

.level-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: linear-gradient(90deg, rgba(0,245,212,0.15), rgba(155,93,229,0.15));
    border: 1px solid rgba(155,93,229,0.4);
    border-radius: 999px; padding: 6px 16px; font-weight: 600;
}
.level-bar-outer {
    width: 100%; height: 10px; border-radius: 999px;
    background: rgba(255,255,255,0.08); overflow: hidden; position: relative; margin-top: 6px;
}
.level-bar-fill {
    height: 100%; border-radius: 999px;
    background: linear-gradient(90deg, #00F5D4, #9B5DE5, #F15BB5);
    background-size: 200% 100%;
    animation: shimmer 3s linear infinite;
}
@keyframes shimmer { 0% {background-position: 0% 0;} 100% {background-position: 200% 0;} }

.streak-flame { font-size: 2.2rem; }
.streak-num { font-size: 1.9rem; font-weight: 700;
    background: linear-gradient(90deg, #FFB703, #FB5607);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

.badge-card {
    text-align: center; padding: 16px 8px; border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.03);
}
.badge-card.unlocked {
    border: 1px solid rgba(0,245,212,0.5);
    background: linear-gradient(160deg, rgba(0,245,212,0.08), rgba(155,93,229,0.08));
    box-shadow: 0 0 22px rgba(0,245,212,0.12);
}
.badge-emoji { font-size: 2.1rem; filter: grayscale(1); opacity: 0.35; }
.badge-card.unlocked .badge-emoji { filter: none; opacity: 1; }
.badge-name { font-weight: 600; margin-top: 6px; font-size: 0.9rem; }
.badge-desc { font-size: 0.75rem; color: #9A93B8; margin-top: 2px; }

.quote-banner {
    border-left: 3px solid #00F5D4; padding: 10px 16px; font-style: italic;
    color: #C9C4E8; background: rgba(255,255,255,0.03); border-radius: 0 12px 12px 0;
}

.stButton>button {
    background: linear-gradient(90deg, #00F5D4, #9B5DE5);
    color: #06060f; font-weight: 700; border: none; border-radius: 12px;
    padding: 0.55em 1.4em; transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(155,93,229,0.35); }

div[data-baseweb="tab-list"] { gap: 4px; }
button[data-baseweb="tab"] { border-radius: 10px 10px 0 0; }

hr { border-color: rgba(255,255,255,0.08) !important; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# DATA HELPERS
# ----------------------------------------------------------------------------

def load_csv(path, columns):
    if os.path.exists(path):
        df = pd.read_csv(path)
        for c in columns:
            if c not in df.columns:
                df[c] = None
        return df[columns]
    return pd.DataFrame(columns=columns)


def save_row(path, columns, row):
    df = load_csv(path, columns)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(path, index=False)


def load_profile():
    cols = ["name", "sex", "age", "height_cm", "weight_kg", "activity_level",
            "goal", "calorie_goal", "protein_goal", "carbs_goal", "fat_goal",
            "water_goal_ml", "steps_goal"]
    df = load_csv(PROFILE_FILE, cols)
    if df.empty:
        return None
    return df.iloc[-1].to_dict()


def save_profile(p):
    pd.DataFrame([p]).to_csv(PROFILE_FILE, index=False)


def calc_bmr(sex, weight_kg, height_cm, age):
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return base + 5 if sex == "Male" else base - 161


def calc_tdee(bmr, activity_level):
    mult = {
        "Sedentary (little/no exercise)": 1.2, "Light (1-3 days/week)": 1.375,
        "Moderate (3-5 days/week)": 1.55, "Active (6-7 days/week)": 1.725,
        "Very Active (athlete/physical job)": 1.9,
    }
    return bmr * mult.get(activity_level, 1.2)


# ----------------------------------------------------------------------------
# GAMIFICATION ENGINE (fully derived from logged data — no extra state to sync)
# ----------------------------------------------------------------------------

def compute_streak(active_dates):
    if not active_dates:
        return 0
    active_set = set(active_dates)
    cursor = date.today()
    if cursor not in active_set:
        cursor -= timedelta(days=1)
    count = 0
    while cursor in active_set:
        count += 1
        cursor -= timedelta(days=1)
    return count


def compute_stats(w_df, n_df, d_df, profile):
    water_goal = profile.get("water_goal_ml", 3000)
    steps_goal = profile.get("steps_goal", 10000)

    water_goal_days = int((d_df["water_ml"] >= water_goal).sum()) if not d_df.empty else 0
    steps_goal_days = int((d_df["steps"] >= steps_goal).sum()) if not d_df.empty else 0
    total_workouts = len(w_df)
    total_food_logs = len(n_df)

    all_dates = set()
    for df in (w_df, n_df, d_df):
        if not df.empty:
            for dstr in df["date"].dropna().unique():
                try:
                    y, m, dd = str(dstr).split("-")
                    all_dates.add(date(int(y), int(m), int(dd)))
                except Exception:
                    pass
    streak = compute_streak(all_dates)

    xp = (total_workouts * 50 + total_food_logs * 15 +
          water_goal_days * 25 + steps_goal_days * 25 + streak * 10)
    level = xp // XP_PER_LEVEL + 1
    xp_into_level = xp % XP_PER_LEVEL

    stats = {
        "total_workouts": total_workouts, "total_food_logs": total_food_logs,
        "water_goal_days": water_goal_days, "steps_goal_days": steps_goal_days,
        "streak": streak, "xp": xp, "level": level,
        "xp_into_level": xp_into_level, "active_days": len(all_dates),
    }
    stats["unlocked_badges"] = {b["id"] for b in BADGES if b["cond"](stats)}
    return stats


def svg_ring(percent, color_from, color_to, center_text, sub_text, ring_id, size=140):
    percent = max(0, min(percent, 1))
    radius = 52
    circumference = 2 * 3.14159265 * radius
    offset = circumference * (1 - percent)
    return f"""
    <div style="text-align:center;">
    <svg width="{size}" height="{size}" viewBox="0 0 120 120">
      <defs>
        <linearGradient id="grad-{ring_id}" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="{color_from}"/>
          <stop offset="100%" stop-color="{color_to}"/>
        </linearGradient>
      </defs>
      <circle cx="60" cy="60" r="{radius}" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="10"/>
      <circle cx="60" cy="60" r="{radius}" fill="none" stroke="url(#grad-{ring_id})" stroke-width="10"
        stroke-linecap="round" stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
        transform="rotate(-90 60 60)" style="transition: stroke-dashoffset 0.6s ease;"/>
      <text x="60" y="56" text-anchor="middle" font-size="20" font-weight="700" fill="#fff">{center_text}</text>
      <text x="60" y="74" text-anchor="middle" font-size="10" fill="#9A93B8">{sub_text}</text>
    </svg>
    </div>
    """


def stat_card(icon, label, value, sub, col):
    with col:
        st.markdown(f"""
        <div class="glass-card">
            <div class="stat-icon">{icon}</div>
            <div class="stat-label">{label}</div>
            <div class="stat-value">{value}</div>
            <div class="stat-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)


PLOTLY_TEMPLATE = "plotly_dark"
NEON = ["#00F5D4", "#9B5DE5", "#F15BB5", "#FEE440", "#6FE7C7"]

# ----------------------------------------------------------------------------
# SIDEBAR — PROFILE
# ----------------------------------------------------------------------------

profile = load_profile()

if LOGO_B64:
    st.sidebar.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px;">
        <img src="data:image/png;base64,{LOGO_B64}" style="height:44px; width:auto;" />
        <div class="grad-title" style="font-size:1.6rem;">CrazyFitness</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown('<div class="grad-title" style="font-size:1.6rem;">⚡ CrazyFitness</div>',
                         unsafe_allow_html=True)
st.sidebar.caption("Level up your fitness, literally.")
st.sidebar.divider()

with st.sidebar.expander("👤 Profile & Goals", expanded=(profile is None)):
    name = st.text_input("Name", value=profile["name"] if profile else "")
    sex = st.selectbox("Sex", ["Male", "Female"],
                        index=0 if not profile or profile["sex"] == "Male" else 1)
    age = st.number_input("Age", 10, 100, int(profile["age"]) if profile else 22)
    height_cm = st.number_input("Height (cm)", 100, 250,
                                 int(profile["height_cm"]) if profile else 170)
    weight_kg = st.number_input("Weight (kg)", 30.0, 250.0,
                                 float(profile["weight_kg"]) if profile else 70.0, step=0.5)
    activity_level = st.selectbox(
        "Activity Level",
        ["Sedentary (little/no exercise)", "Light (1-3 days/week)",
         "Moderate (3-5 days/week)", "Active (6-7 days/week)",
         "Very Active (athlete/physical job)"], index=2)
    goal = st.selectbox("Goal", ["Lose Fat", "Maintain", "Build Muscle"], index=1)

    bmr = calc_bmr(sex, weight_kg, height_cm, age)
    tdee = calc_tdee(bmr, activity_level)
    calorie_goal_default = tdee - 500 if goal == "Lose Fat" else (tdee + 300 if goal == "Build Muscle" else tdee)

    st.caption(f"BMR **{bmr:.0f}** kcal · TDEE **{tdee:.0f}** kcal")
    calorie_goal = st.number_input("Daily Calorie Goal", 800, 6000, int(calorie_goal_default), step=50)
    protein_goal = st.number_input("Protein Goal (g)", 0, 400, int(weight_kg * 1.8))
    carbs_goal = st.number_input("Carbs Goal (g)", 0, 800, int((calorie_goal * 0.4) / 4))
    fat_goal = st.number_input("Fat Goal (g)", 0, 300, int((calorie_goal * 0.25) / 9))
    water_goal_ml = st.number_input("Water Goal (ml)", 500, 6000, 3000, step=250)
    steps_goal = st.number_input("Steps Goal", 1000, 30000, 10000, step=500)

    if st.button("💾 Save Profile", use_container_width=True):
        save_profile({
            "name": name, "sex": sex, "age": age, "height_cm": height_cm,
            "weight_kg": weight_kg, "activity_level": activity_level, "goal": goal,
            "calorie_goal": calorie_goal, "protein_goal": protein_goal,
            "carbs_goal": carbs_goal, "fat_goal": fat_goal,
            "water_goal_ml": water_goal_ml, "steps_goal": steps_goal,
        })
        st.success("Profile saved!")
        st.rerun()

if profile is None:
    st.sidebar.warning("⚠️ Set up & save your profile to unlock your dashboard.")
    profile = {"name": "", "calorie_goal": 2200, "protein_goal": 130, "carbs_goal": 220,
               "fat_goal": 60, "water_goal_ml": 3000, "steps_goal": 10000, "weight_kg": 70}

# Live stats for sidebar gamification snapshot
w_df_all = load_csv(WORKOUTS_FILE, ["date", "activity", "duration_min", "calories_burned", "notes"])
n_df_all = load_csv(NUTRITION_FILE, ["date", "meal", "food", "calories", "protein", "carbs", "fat"])
d_df_all = load_csv(DAILY_FILE, ["date", "steps", "water_ml"])
stats = compute_stats(w_df_all, n_df_all, d_df_all, profile)

st.sidebar.divider()
st.sidebar.markdown(f"""
<div class="level-badge">🎮 Level {stats['level']}</div>
<div class="level-bar-outer"><div class="level-bar-fill" style="width:{stats['xp_into_level']/XP_PER_LEVEL*100:.0f}%"></div></div>
<div class="subtle" style="margin-top:4px;">{stats['xp_into_level']} / {XP_PER_LEVEL} XP</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div style="margin-top:14px; display:flex; align-items:center; gap:10px;">
  <span class="streak-flame">🔥</span>
  <div><span class="streak-num">{stats['streak']}</span> <span class="subtle">day streak</span></div>
</div>
""", unsafe_allow_html=True)

st.sidebar.divider()
selected_date = st.sidebar.date_input("📅 Log date", value=date.today())

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------

greeting = f", {profile['name']}" if profile.get("name") else ""
if LOGO_B64:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:16px;">
        <img src="data:image/png;base64,{LOGO_B64}" style="height:64px; width:auto;" />
        <div class="grad-title">CrazyFitness{greeting}</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f'<div class="grad-title">⚡ CrazyFitness{greeting}</div>', unsafe_allow_html=True)
st.markdown('<div class="subtle">Log it. Level up. Don\'t break the streak.</div>', unsafe_allow_html=True)

quote = QUOTES[int(selected_date.strftime("%j")) % len(QUOTES)]
st.markdown(f'<div class="quote-banner" style="margin-top:14px;">"{quote}"</div>', unsafe_allow_html=True)
st.write("")

tab_dashboard, tab_workout, tab_nutrition, tab_daily, tab_badges, tab_history = st.tabs(
    ["📊 Dashboard", "🏋️ Workout", "🍎 Food & Macros", "🚶 Steps & Water", "🎖️ Badges", "📜 History"]
)

# ----------------------------------------------------------------------------
# HELPER: celebrate level-ups / new badges after an action
# ----------------------------------------------------------------------------

def celebrate_if_earned(stats_before, stats_after):
    if stats_after["level"] > stats_before["level"]:
        st.balloons()
        st.toast(f"🎉 Level Up! You're now Level {stats_after['level']}!", icon="🎮")
    new_badges = stats_after["unlocked_badges"] - stats_before["unlocked_badges"]
    for bid in new_badges:
        b = next(x for x in BADGES if x["id"] == bid)
        st.toast(f"{b['emoji']} Badge unlocked: {b['name']}!", icon="🎖️")
        st.balloons()


# ----------------------------------------------------------------------------
# TAB: WORKOUT
# ----------------------------------------------------------------------------

with tab_workout:
    st.subheader("Log a Workout")
    col1, col2 = st.columns(2)
    with col1:
        activity = st.selectbox("Activity Type", list(MET_VALUES.keys()))
        duration_min = st.slider("Duration (minutes)", 5, 240, 30, step=5)
    with col2:
        notes = st.text_input("Notes (optional)", placeholder="e.g. leg day, new PB")
        auto_cal = MET_VALUES[activity] * float(profile.get("weight_kg", 70)) * (duration_min / 60)
        st.markdown(f"""
        <div class="glass-card"><div class="stat-label">Estimated Burn</div>
        <div class="stat-value">🔥 {auto_cal:.0f} kcal</div>
        <div class="stat-sub">+50 XP for logging</div></div>
        """, unsafe_allow_html=True)

    if st.button("➕ Add Workout", type="primary"):
        before = compute_stats(w_df_all, n_df_all, d_df_all, profile)
        save_row(WORKOUTS_FILE, ["date", "activity", "duration_min", "calories_burned", "notes"],
                 {"date": str(selected_date), "activity": activity, "duration_min": duration_min,
                  "calories_burned": round(auto_cal), "notes": notes})
        w_df_all2 = load_csv(WORKOUTS_FILE, ["date", "activity", "duration_min", "calories_burned", "notes"])
        after = compute_stats(w_df_all2, n_df_all, d_df_all, profile)
        st.success(f"Logged {duration_min} min of {activity} 🔥 +50 XP")
        celebrate_if_earned(before, after)
        st.rerun()

    st.divider()
    st.caption("Today's workouts")
    today_w = w_df_all[w_df_all["date"] == str(selected_date)]
    if today_w.empty:
        st.info("No workouts logged yet for this date.")
    else:
        st.dataframe(today_w, use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------------
# TAB: FOOD & MACROS
# ----------------------------------------------------------------------------

with tab_nutrition:
    st.subheader("Log Food")
    quick_pick = st.selectbox("⚡ Quick-add", list(QUICK_FOODS.keys()))
    prefill = QUICK_FOODS[quick_pick] or {"cal": 0, "protein": 0, "carbs": 0, "fat": 0}
    food_name_default = "" if quick_pick.startswith("--") else quick_pick

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        food_name = st.text_input("Food name", value=food_name_default)
        meal_type = st.selectbox("Meal", ["Breakfast", "Lunch", "Dinner", "Snack"])
    with col2:
        cal = st.number_input("Calories (kcal)", 0, 3000, int(prefill["cal"]))
        protein = st.number_input("Protein (g)", 0, 300, int(prefill["protein"]))
    with col3:
        carbs = st.number_input("Carbs (g)", 0, 500, int(prefill["carbs"]))
        fat = st.number_input("Fat (g)", 0, 200, int(prefill["fat"]))

    if st.button("➕ Add Food Entry", type="primary"):
        if food_name.strip() == "":
            st.error("Please enter a food name.")
        else:
            before = compute_stats(w_df_all, n_df_all, d_df_all, profile)
            save_row(NUTRITION_FILE, ["date", "meal", "food", "calories", "protein", "carbs", "fat"],
                     {"date": str(selected_date), "meal": meal_type, "food": food_name,
                      "calories": cal, "protein": protein, "carbs": carbs, "fat": fat})
            n_df_all2 = load_csv(NUTRITION_FILE, ["date", "meal", "food", "calories", "protein", "carbs", "fat"])
            after = compute_stats(w_df_all, n_df_all2, d_df_all, profile)
            st.success(f"Added {food_name} to {meal_type} 🍽️ +15 XP")
            celebrate_if_earned(before, after)
            st.rerun()

    st.divider()
    st.caption("Today's food log")
    today_n = n_df_all[n_df_all["date"] == str(selected_date)]
    if today_n.empty:
        st.info("No food logged yet for this date.")
    else:
        st.dataframe(today_n, use_container_width=True, hide_index=True)
        totals = today_n[["calories", "protein", "carbs", "fat"]].sum()
        c1, c2, c3, c4 = st.columns(4)
        stat_card("🔥", "Calories", f"{totals['calories']:.0f}", "kcal today", c1)
        stat_card("🥩", "Protein", f"{totals['protein']:.0f}g", "", c2)
        stat_card("🍞", "Carbs", f"{totals['carbs']:.0f}g", "", c3)
        stat_card("🥑", "Fat", f"{totals['fat']:.0f}g", "", c4)

# ----------------------------------------------------------------------------
# TAB: STEPS & WATER
# ----------------------------------------------------------------------------

with tab_daily:
    st.subheader("Steps & Water Intake")
    existing = d_df_all[d_df_all["date"] == str(selected_date)]
    cur_steps = int(existing["steps"].iloc[-1]) if not existing.empty else 0
    cur_water = int(existing["water_ml"].iloc[-1]) if not existing.empty else 0

    col1, col2 = st.columns(2)
    with col1:
        steps = st.slider("👣 Steps today", 0, 30000, cur_steps, step=100)
        st.markdown(svg_ring(steps / max(profile.get("steps_goal", 10000), 1), "#00F5D4", "#6FE7C7",
                              f"{steps:,}", "steps", "steps_ring"), unsafe_allow_html=True)
    with col2:
        water_ml = st.slider("💧 Water intake (ml)", 0, 6000, cur_water, step=100)
        st.markdown(svg_ring(water_ml / max(profile.get("water_goal_ml", 3000), 1), "#4CC9F0", "#4361EE",
                              f"{water_ml}", "ml", "water_ring"), unsafe_allow_html=True)

    if st.button("💾 Save Today's Steps & Water", type="primary"):
        before = compute_stats(w_df_all, n_df_all, d_df_all, profile)
        d_new = d_df_all[d_df_all["date"] != str(selected_date)]
        d_new = pd.concat([d_new, pd.DataFrame([{"date": str(selected_date), "steps": steps, "water_ml": water_ml}])],
                           ignore_index=True)
        d_new.to_csv(DAILY_FILE, index=False)
        after = compute_stats(w_df_all, n_df_all, d_new, profile)
        st.success("Saved! 🚶💧 +25 XP for each goal hit")
        celebrate_if_earned(before, after)
        st.rerun()

# ----------------------------------------------------------------------------
# TAB: BADGES
# ----------------------------------------------------------------------------

with tab_badges:
    st.subheader(f"🎖️ Badges — {len(stats['unlocked_badges'])} / {len(BADGES)} unlocked")
    cols = st.columns(5)
    for i, b in enumerate(BADGES):
        unlocked = b["id"] in stats["unlocked_badges"]
        with cols[i % 5]:
            st.markdown(f"""
            <div class="badge-card {'unlocked' if unlocked else ''}">
                <div class="badge-emoji">{b['emoji']}</div>
                <div class="badge-name">{b['name']}</div>
                <div class="badge-desc">{b['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            st.write("")

# ----------------------------------------------------------------------------
# TAB: DASHBOARD
# ----------------------------------------------------------------------------

with tab_dashboard:
    st.subheader(f"Dashboard — {selected_date.strftime('%A, %d %B %Y')}")

    today_w = w_df_all[w_df_all["date"] == str(selected_date)]
    today_n = n_df_all[n_df_all["date"] == str(selected_date)]
    today_d = d_df_all[d_df_all["date"] == str(selected_date)]

    cals_in = today_n["calories"].sum() if not today_n.empty else 0
    cals_out = today_w["calories_burned"].sum() if not today_w.empty else 0
    steps_today = int(today_d["steps"].iloc[-1]) if not today_d.empty else 0
    water_today = int(today_d["water_ml"].iloc[-1]) if not today_d.empty else 0
    net_cals = cals_in - cals_out
    cal_goal = profile.get("calorie_goal", 2200)

    c1, c2, c3, c4, c5 = st.columns(5)
    stat_card("🔥", "Calories In", f"{cals_in:.0f}", f"Goal {cal_goal:.0f} kcal", c1)
    stat_card("⚡", "Burned", f"{cals_out:.0f}", "kcal", c2)
    stat_card("🎯", "Net", f"{net_cals:.0f}", f"{cal_goal - net_cals:.0f} remaining", c3)
    stat_card("👣", "Steps", f"{steps_today:,}", f"Goal {profile.get('steps_goal', 10000):,}", c4)
    stat_card("💧", "Water", f"{water_today} ml", f"Goal {profile.get('water_goal_ml', 3000)} ml", c5)

    st.write("")
    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown(svg_ring(cals_in / max(cal_goal, 1), "#F15BB5", "#9B5DE5",
                              f"{cals_in:.0f}", "kcal in", "dash_cal"), unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;" class="subtle">Calories</div>', unsafe_allow_html=True)
    with r2:
        st.markdown(svg_ring(steps_today / max(profile.get("steps_goal", 10000), 1), "#00F5D4", "#6FE7C7",
                              f"{steps_today:,}", "steps", "dash_steps"), unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;" class="subtle">Steps</div>', unsafe_allow_html=True)
    with r3:
        st.markdown(svg_ring(water_today / max(profile.get("water_goal_ml", 3000), 1), "#4CC9F0", "#4361EE",
                              f"{water_today}", "ml", "dash_water"), unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;" class="subtle">Water</div>', unsafe_allow_html=True)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Macro Breakdown (Today)**")
        totals = today_n[["protein", "carbs", "fat"]].sum() if not today_n.empty else pd.Series(
            {"protein": 0, "carbs": 0, "fat": 0})
        if totals.sum() > 0:
            macro_df = pd.DataFrame({
                "Macro": ["Protein", "Carbs", "Fat"],
                "Calories": [totals["protein"] * 4, totals["carbs"] * 4, totals["fat"] * 9],
            })
            fig = px.pie(macro_df, names="Macro", values="Calories", hole=0.55,
                         color="Macro", template=PLOTLY_TEMPLATE,
                         color_discrete_map={"Protein": "#F15BB5", "Carbs": "#00F5D4", "Fat": "#FEE440"})
            fig.update_traces(textinfo="label+percent")
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320,
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Log some food to see your macro breakdown.")

    with col2:
        st.markdown("**Net Calories vs Goal**")
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number+delta", value=net_cals, delta={"reference": cal_goal},
            gauge={"axis": {"range": [0, max(cal_goal * 1.4, net_cals * 1.1, 500)]},
                   "bar": {"color": "#9B5DE5"},
                   "steps": [{"range": [0, cal_goal], "color": "rgba(0,245,212,0.12)"},
                             {"range": [cal_goal, cal_goal * 1.4], "color": "rgba(241,91,181,0.12)"}],
                   "threshold": {"line": {"color": "#F15BB5", "width": 3}, "value": cal_goal}},
        ))
        fig2.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=320, template=PLOTLY_TEMPLATE,
                            paper_bgcolor="rgba(0,0,0,0)", font_color="#EDEDFB")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.markdown("**📈 Weekly Trends**")
    if not d_df_all.empty or not n_df_all.empty or not w_df_all.empty:
        all_dates = pd.to_datetime(pd.concat([d_df_all["date"], n_df_all["date"], w_df_all["date"]]).dropna().unique())
        if len(all_dates) > 0:
            last7 = sorted(all_dates)[-7:]
            rows = []
            for d in last7:
                d_str = d.strftime("%Y-%m-%d")
                rows.append({
                    "Date": d_str,
                    "Calories In": n_df_all[n_df_all["date"] == d_str]["calories"].sum(),
                    "Calories Burned": w_df_all[w_df_all["date"] == d_str]["calories_burned"].sum(),
                    "Steps": int(d_df_all[d_df_all["date"] == d_str]["steps"].iloc[-1])
                             if not d_df_all[d_df_all["date"] == d_str].empty else 0,
                })
            trend_df = pd.DataFrame(rows)
            fig3 = px.line(trend_df, x="Date", y=["Calories In", "Calories Burned"], markers=True,
                            template=PLOTLY_TEMPLATE, color_discrete_sequence=["#F15BB5", "#00F5D4"])
            fig3.update_layout(height=300, margin=dict(t=20, b=10, l=10, r=10), yaxis_title="kcal",
                                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig3, use_container_width=True)

            fig4 = px.bar(trend_df, x="Date", y="Steps", template=PLOTLY_TEMPLATE,
                           color_discrete_sequence=["#9B5DE5"])
            fig4.add_hline(y=profile.get("steps_goal", 10000), line_dash="dash", line_color="#F15BB5",
                            annotation_text="Goal")
            fig4.update_layout(height=280, margin=dict(t=20, b=10, l=10, r=10),
                                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Log data across a few days to unlock weekly trend charts.")

# ----------------------------------------------------------------------------
# TAB: HISTORY
# ----------------------------------------------------------------------------

with tab_history:
    st.subheader("Full History & Data Export")
    h1, h2, h3 = st.tabs(["Workouts", "Nutrition", "Steps & Water"])
    with h1:
        st.dataframe(w_df_all.sort_values("date", ascending=False), use_container_width=True, hide_index=True)
        if not w_df_all.empty:
            st.download_button("⬇️ Download workouts.csv", w_df_all.to_csv(index=False), "workouts.csv", "text/csv")
    with h2:
        st.dataframe(n_df_all.sort_values("date", ascending=False), use_container_width=True, hide_index=True)
        if not n_df_all.empty:
            st.download_button("⬇️ Download nutrition.csv", n_df_all.to_csv(index=False), "nutrition.csv", "text/csv")
    with h3:
        st.dataframe(d_df_all.sort_values("date", ascending=False), use_container_width=True, hide_index=True)
        if not d_df_all.empty:
            st.download_button("⬇️ Download daily_log.csv", d_df_all.to_csv(index=False), "daily_log.csv", "text/csv")

st.write("")
st.markdown('<div class="subtle" style="text-align:center;">CrazyFitness— built with Streamlit, Pandas & Plotly ⚡</div>',
            unsafe_allow_html=True)