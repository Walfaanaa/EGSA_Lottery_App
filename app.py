import streamlit as st
import pandas as pd
from io import BytesIO
import time
import os
from dotenv import load_dotenv

# -------------------------------
# 1️⃣ Page Setup
# -------------------------------
st.set_page_config(
    page_title="🎟️ EGSA Lottery Winners",
    layout="wide",
    page_icon="🎟️"
)

# -------------------------------
# 🎨 Custom Blue UI Style
# -------------------------------
st.markdown(
    """
    <style>
    /* Full page background */
    body {
        background-color: #1E90FF;  /* Dodger Blue page background */
    }
    [data-testid="stAppViewContainer"] {
        background-color: #1E90FF;
    }
    /* Tables */
    .dataframe, .stDataFrame>div>div>div>div>table {
        background-color: #87CEFA !important; /* Light Sky Blue for tables */
        color: #000000 !important; /* Black text for readability */
    }
    /* Custom warning box */
    .custom-warning {
        background-color: #104E8B;  /* Dark Blue */
        color: #00FFFF;  /* Cyan text */
        padding: 10px;
        border-radius: 5px;
        text-align: left;
        margin-bottom: 10px;
        font-weight: bold;
    }
    /* 🎨 Main Header Section */
    .header-section {
        background-color: #4169E1;  /* Royal Blue */
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;  /* White text for contrast */
        font-family: Arial, sans-serif;
    }
    /* Center all h1 headers */
    h1, h3 {
        text-align: center;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# 🎨 Header Section with Red Background
# -------------------------------
st.markdown(
    """
    <style>
    /* Header section styling */
    .header-section {
        background-color: red;  /* Red background */
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;  /* White text for contrast */
        font-family: Arial, sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="header-section">
        <h1>🎟️ EGSA Lottery Winners App (Authorized & One-Time Draw)</h1>
        <h3>Welcome to the EGSA Lottery Winners App</h3>
        <p>This system ensures fair, transparent, and one-time-only draws managed by authorized personnel.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# 2️⃣ Load Members Data
# -------------------------------
DATA_FILE = "members_data.xlsx"
WINNER_FILE = "winners_record.xlsx"

try:
    members_df = pd.read_excel(DATA_FILE)
    st.success(f"✅ {len(members_df)} members loaded successfully from admin file.")
    st.dataframe(members_df)  # Blue table background applied
except FileNotFoundError:
    st.error("❌ members_data.xlsx file not found! Please upload it to your app folder or GitHub repo.")
    st.stop()

# -------------------------------
# 3️⃣ Load Passwords from .env
# -------------------------------
load_dotenv()

AUTHORIZED_CODE = os.getenv("STREAMLIT_ADMIN_PASSWORD")
RESET_PASSWORD = os.getenv("STREAMLIT_RESET_PASSWORD")

# Display warnings with custom style
if AUTHORIZED_CODE is None:
    st.markdown('<div class="custom-warning">⚠️ Admin password not set! Add STREAMLIT_ADMIN_PASSWORD to your .env file.</div>', unsafe_allow_html=True)
if RESET_PASSWORD is None:
    st.markdown('<div class="custom-warning">⚠️ Reset password not set! Add STREAMLIT_RESET_PASSWORD to your .env file.</div>', unsafe_allow_html=True)

# -------------------------------
# 4️⃣ Admin Authorization
# -------------------------------
password = st.text_input("Enter admin passcode to enable draw:", type="password")

if password == AUTHORIZED_CODE:

    st.success("Access granted! You can now enable the draw.")

    # Reset Section Using .env PASSWORD
    if os.path.exists(WINNER_FILE):

        with st.expander("⚙️ Admin Reset Options"):

            st.warning("⚠️ A previous draw has already been conducted.")

            reset_pass_input = st.text_input(
                "Enter reset password to reset draw",
                type="password"
            )

            if st.button("🔄 Reset for New Round (Admin Only)"):

                if reset_pass_input == RESET_PASSWORD:
                    os.remove(WINNER_FILE)
                    st.success("✅ Winners record deleted. You can now run a new draw.")
                    st.experimental_rerun()
                else:
                    st.error("❌ Incorrect reset password.")

        # Show previous winners
        previous_winners = pd.read_excel(WINNER_FILE)
        st.subheader("🎉 Previous Winners")
        st.dataframe(previous_winners)  # Blue table background

    # Pick Winners
    else:

        num_winners = st.number_input(
            "🏆 Number of winners to select",
            min_value=1,
            max_value=len(members_df),
            value=1
        )

        if st.button("🎲 Pick Winners"):

            placeholder = st.empty()

            with placeholder.container():

                st.info("Picking winners... Please wait.")

                progress_text = st.empty()
                progress_bar = st.progress(0)

                for i in range(101):
                    time.sleep(0.01)
                    progress_text.text(f"Progress: {i}%")
                    progress_bar.progress(i)

                winners = members_df.sample(n=num_winners).reset_index(drop=True)

                st.success("🎉 Winners Selected!")
                st.balloons()
                st.subheader("🎉 Winners List")
                st.dataframe(winners)  # Blue table background

                # Save winners record
                winners.to_excel(WINNER_FILE, index=False)

                # Download winners
                def convert_df_to_excel(df):
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                        df.to_excel(writer, index=False, sheet_name="Winners")
                    return output.getvalue()

                excel_data = convert_df_to_excel(winners)

                st.download_button(
                    label="💾 Download Winners as Excel",
                    data=excel_data,
                    file_name="EGSA_lottery_winners.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

else:
    if password:
        st.error("❌ Invalid passcode. Access denied.")
    st.info("You can view the member list, but only authorized staff can pick winners.")

