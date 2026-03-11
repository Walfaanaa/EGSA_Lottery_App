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
# 🎨 Background Color + Text Styling
# -------------------------------
st.markdown(
    """
    <style>
    /* Full page background */
    body {
        background-color: #f0f8ff;  /* Light blue background */
    }
    /* Main container styling */
    [data-testid="stAppViewContainer"] {
        background-color: #f0f8ff;
    }
    /* Titles and headers */
    h1, h3 {
        color: #000000;
        text-align: center;
    }
    /* Paragraph text */
    p {
        color: green;
        font-size: 18px;
        text-align: center;
    }
    /* Style tables */
    .dataframe {
        background-color: #ffffff; /* White table background */
        color: #000000; /* Text color */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# 🎨 Centered Welcome + Green Description
# -------------------------------
st.title("🎟️ EGSA Lottery Winners App (Authorized & One-Time Draw)")

st.markdown(
    """
    <h3>Welcome to the <b>EGSA Lottery Winners App</b></h3>
    <p>This system ensures fair, transparent, and one-time-only draws managed by authorized personnel.</p>
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
    st.dataframe(members_df)
except FileNotFoundError:
    st.error("❌ members_data.xlsx file not found! Please upload it to your app folder or GitHub repo.")
    st.stop()

# -------------------------------
# 3️⃣ Load Passwords from .env
# -------------------------------
load_dotenv()

AUTHORIZED_CODE = os.getenv("STREAMLIT_ADMIN_PASSWORD")
RESET_PASSWORD = os.getenv("STREAMLIT_RESET_PASSWORD")

if AUTHORIZED_CODE is None:
    st.warning("⚠️ Admin password not set! Add STREAMLIT_ADMIN_PASSWORD to your .env file.")
if RESET_PASSWORD is None:
    st.warning("⚠️ Reset password not set! Add STREAMLIT_RESET_PASSWORD to your .env file.")

# -------------------------------
# 4️⃣ Admin Authorization
# -------------------------------
password = st.text_input("Enter admin passcode to enable draw:", type="password")

if password == AUTHORIZED_CODE:

    st.success("Access granted! You can now enable the draw.")

    # -------------------------------
    # Reset Section Using .env PASSWORD
    # -------------------------------
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
        st.dataframe(previous_winners)

    # -------------------------------
    # Pick Winners
    # -------------------------------
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
                st.dataframe(winners)

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
