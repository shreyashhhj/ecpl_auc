import base64
import json
import os
import pandas as pd
import streamlit as st

# --- PAGE CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="ECPL 2026 Live Auction Tracker", page_icon="🏏", layout="wide"
)


def get_base64_of_bin_file(bin_file):
  try:
    with open(bin_file, "rb") as f:
      data = f.read()
    return base64.b64encode(data).decode()
  except Exception:
    return ""


bin_str = get_base64_of_bin_file("bg.jpeg")
if bin_str:
  bg_css = f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.55), rgba(0, 0, 0, 0.55)), url("data:image/jpeg;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        color: #ffffff;
    }}
    .stMetric {{
        background-color: rgba(22, 27, 34, 0.9);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #30363d;
    }}
    .assignment-box {{
        background-color: rgba(22, 27, 34, 0.88);
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #484f58;
        margin-bottom: 20px;
    }}
    </style>
    """
else:
  bg_css = """
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    </style>
    """

st.markdown(bg_css, unsafe_allow_html=True)

TOTAL_PURSE_CR = 100.0  # 100 Crores

# --- 8 TEAMS LIST ---
team_list = [
    "Phantom Blues",
    "White Falcons",
    "Granite Gladiators",
    "Rising Champions",
    "Red Raptors",
    "Team Pirates",
    "Gold Gangsters",
    "Mighty Mavericks",
]

# --- OFFICIAL LEADERSHIP ---
team_leadership = {
    "Phantom Blues": {"c": "Shreyash Jaiswal", "vc": "Aahana Kapse"},
    "White Falcons": {"c": "Vedant Karande", "vc": "Divya Tiwari"},
    "Granite Gladiators": {"c": "Paresh Dube", "vc": "Jhanvi Bhusare"},
    "Rising Champions": {"c": "Aziz Azad", "vc": "Sharvori Gawande"},
    "Red Raptors": {"c": "Swayam Tiwari", "vc": "Thalisha Godhani"},
    "Team Pirates": {"c": "Prasad Akle", "vc": "Jiya Kurjekar"},
    "Gold Gangsters": {"c": "Ansh Bisen", "vc": "Palak Jane"},
    "Mighty Mavericks": {"c": "Aarav Shukla", "vc": "Mahek Mishra"},
}

STATE_FILE = "auction_state.json"


# Load or Initialize Players Data from Renamed Excel & JSON Persistence
def load_data():
  excel_file = "players.xlsx"
  try:
    df_raw = pd.read_excel(excel_file)
    base_players = []
    for idx, row in df_raw.iterrows():
      base_players.append({
          "ID": idx + 1,
          "Name": str(row.get("Full Name", "")).strip(),
          "Year": str(row.get("Year of Study", "")).strip() + " Year",
          "Role": str(row.get("Player Primary Role", "")).strip(),
          "Select Team": "Available",
          "Price (Cr)": 0.0,
      })
    df_default = pd.DataFrame(base_players)
  except Exception as e:
    st.error(
        f"Error loading Excel file '{excel_file}': {e}. Please ensure"
        " 'players.xlsx' is uploaded."
    )
    df_default = pd.DataFrame(
        columns=["ID", "Name", "Year", "Role", "Select Team", "Price (Cr)"]
    )

  if os.path.exists(STATE_FILE):
    try:
      with open(STATE_FILE, "r") as f:
        saved_data = json.load(f)
        return pd.DataFrame(saved_data)
    except Exception:
      return df_default
  return df_default


def save_data(df):
  with open(STATE_FILE, "w") as f:
    json.dump(df.to_dict(orient="records"), f)


if "players_df" not in st.session_state:
  st.session_state.players_df = load_data()

# --- RE-CALCULATE TEAMS & PURSE ---
current_teams = {}
for t in team_list:
  c_name = team_leadership[t]["c"]
  vc_name = team_leadership[t]["vc"]
  current_teams[t] = {
      "captain": c_name,
      "vc": vc_name,
      "purse": TOTAL_PURSE_CR,
      "squad": [
          {"Name": f"{c_name} (C)", "Price": 0.0, "Role": "Captain"},
          {"Name": f"{vc_name} (VC)", "Price": 0.0, "Role": "VC"},
      ],
  }

for _, row in st.session_state.players_df.iterrows():
  assigned_t = row["Select Team"]
  p_price = float(row["Price (Cr)"])
  if assigned_t != "Available" and assigned_t in current_teams:
    current_teams[assigned_t]["purse"] -= p_price
    current_teams[assigned_t]["squad"].append({
        "Name": row["Name"],
        "Role": row["Role"],
        "Price": p_price,
    })

st.session_state.teams = current_teams

# --- SIDEBAR CONTROLS ---
st.sidebar.title("⚙️ Controls")
if st.sidebar.button("🔄 Reset All Data"):
  if os.path.exists(STATE_FILE):
    os.remove(STATE_FILE)
  st.session_state.clear()
  st.success("All data successfully reset!")
  st.rerun()

# --- MAIN HEADER ---
st.title("⚡ ECPL 2026 — Live Auction Tracker 🏏")
st.markdown("Multi-Device Live Sync Dashboard")
st.markdown("---")

# --- PHANTOM BLUES DASHBOARD ---
pb_data = st.session_state.teams["Phantom Blues"]
pb_spent = TOTAL_PURSE_CR - pb_data["purse"]
st.subheader("🔥 Your Team: Phantom Blues Dashboard")
c1, c2, c3 = st.columns(3)
c1.metric("Remaining Purse", f"₹ {pb_data['purse']:.2f} Cr")
c2.metric("Total Spent", f"₹ {pb_spent:.2f} Cr")
c3.metric("Squad Size", f"{len(pb_data['squad'])} Players")

with st.expander("🛡️️ View Phantom Blues Squad Details"):
  for p in pb_data["squad"]:
    st.text(
        f"• {p['Name']} — Role: {p.get('Role', 'Player')} (Price: ₹"
        f" {p.get('Price', 0.0):.2f} Cr)"
    )

st.markdown("---")

# --- QUICK BIDDING PANEL ---
st.subheader("📝 Assign / Manage Team Squads")
st.markdown('<div class="assignment-box">', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
df = st.session_state.players_df
available_df = df[df["Select Team"] == "Available"]
available_players = available_df["Name"].tolist()

with col1:
  selected_team = st.selectbox(
      "🛡️ Select Team:", list(st.session_state.teams.keys())
  )

with col2:
  if available_players:
    selected_player = st.selectbox(
        "👤 Select Available Player:", available_players
    )
  else:
    selected_player = None
    st.info("All registered players have been assigned!")

with col3:
  sold_price = st.number_input(
      "💰 Sold Price (Cr):",
      min_value=0.0,
      max_value=100.0,
      step=0.1,
      value=0.5,
      format="%.2f",
  )

st.markdown("<br>", unsafe_allow_html=True)

if selected_player:
  if st.button(
      "⚡ Confirm & Assign Player", type="primary", use_container_width=True
  ):
    current_purse = st.session_state.teams[selected_team]["purse"]
    if current_purse >= sold_price:
      idx = df[df["Name"] == selected_player].index[0]
      st.session_state.players_df.at[idx, "Select Team"] = selected_team
      st.session_state.players_df.at[idx, "Price (Cr)"] = sold_price

      # Save state for cross-device sync
      save_data(st.session_state.players_df)

      st.success(
          f"✅ {selected_player} successfully assigned to {selected_team} for ₹"
          f" {sold_price:.2f} Cr!"
      )
      st.rerun()
    else:
      st.error(f"❌ {selected_team} does not have enough remaining purse!")

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")

# --- ALL TEAMS OVERVIEW ---
st.subheader("📊 All 8 Teams Status Overview")
t_names = list(st.session_state.teams.keys())
for i in range(0, len(t_names), 4):
  cols = st.columns(4)
  for j in range(4):
    if i + j < len(t_names):
      t = t_names[i + j]
      data = st.session_state.teams[t]
      spent = TOTAL_PURSE_CR - data["purse"]
      with cols[j]:
        st.markdown(f"### **{t}**")
        st.metric("Purse Left", f"₹ {data['purse']:.2f} Cr", f"-₹ {spent:.2f} Cr")
        st.write(f"👥 Squad: {len(data['squad'])} Players")
        with st.expander(f"View {t}"):
          for sp in data["squad"]:
            st.text(
                f"- {sp['Name']}"
                + (
                    f" (₹ {sp.get('Price', 0.0):.2f} Cr)"
                    if sp.get("Price", 0.0) > 0
                    else ""
                )
            )
  st.markdown("---")

# --- MASTER TABLE EDITOR ---
st.subheader("📋 Master Player Directory & Table")
team_options = ["Available"] + team_list
edited_df = st.data_editor(
    st.session_state.players_df,
    column_config={
        "Select Team": st.column_config.SelectboxColumn(
            "Assign Team", options=team_options, required=True
        ),
        "Price (Cr)": st.column_config.NumberColumn(
            "Price (Cr)", min_value=0.0, max_value=100.0, step=0.1, format="%.2f"
        ),
    },
    disabled=["ID", "Name", "Year", "Role"],
    hide_index=True,
    use_container_width=True,
)

if st.button("💾 Update All Changes"):
  st.session_state.players_df = edited_df
  save_data(edited_df)
  st.success("🎉 All team squads and purses updated successfully!")
  st.rerun()