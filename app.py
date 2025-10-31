# -----------------------------------
# 🎟️ EGSA Lottery Winners (Authorized One-Time Draw with Admin Reset)
# -----------------------------------

import streamlit as st
import pandas as pd
from io import BytesIO
import time
import os

# -------------------------------
# 1️⃣ Page Setup
# -------------------------------
st.set_page_config(
    page_title="🎟️ EGSA Lottery Winners",
    layout="wide",
    page_icon="🎟️"
)

st.title("🎟️ EGSA Lottery Winners App (Authorized & One-Time Draw)")
st.markdown("""
Welcome to the **EGSA Lottery Winners App**.  
This system ensures fair, transparent, and one-time-only draws managed by authorized personnel.
""")

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
# 3️⃣ Admin Authorization
# -------------------------------
st.subheader("🔑 Authorized Draw Access")

password = st.text_input("Enter admin passcode to enable draw:", type="password")

AUTHORIZED_CODE = "EGSA2025!"  # 🔒 Change this to your private code

# -------------------------------
# 4️⃣ If Authorized
# -------------------------------
if password == AUTHORIZED_CODE:
    st.success("✅ Access granted. You can now perform the draw or manage results.")

    # -----------------------------------
    # 🔁 Optional: Admin Reset for Next Round
    # -----------------------------------
    if os.path.exists(WINNER_FILE):
        with st.expander("⚙️ Admin Reset Options"):
            st.warning("⚠️ A previous draw has already been conducted.")
            if st.button("🔄 Reset for New Round (Admin Only)"):
                os.remove(WINNER_FILE)
                st.success("✅ Winners record deleted. You can now run a new draw.")
                st.experimental_rerun()

        # Show previous winners
        st.subheader("🎉 Previous Winners")
        previous_winners = pd.read_excel(WINNER_FILE)
        st.dataframe(previous_winners)

    else:
        # -------------------------------
        # 5️⃣ Select Number of Winners
        # -------------------------------
        num_winners = st.number_input(
            "🏆 Number of winners to select",
            min_value=1,
            max_value=len(members_df),
            value=1
        )

        # -------------------------------
        # 6️⃣ Pick Winners (One-Time Only)
        # -------------------------------
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
                st.subheader("🎉 Winners List")
                st.dataframe(winners)

                # Save winners record permanently (locks future draws)
                winners.to_excel(WINNER_FILE, index=False)

            # -------------------------------
            # 7️⃣ Download Winners
            # -------------------------------
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

# -------------------------------
# 8️⃣ If Not Authorized
# -------------------------------
else:
    if password:
        st.error("❌ Invalid passcode. Access denied.")
    st.info("You can view the member list, but only authorized staff can pick winners.")

# -------------------------------
# 🧩 Admin Note
# -------------------------------
st.markdown("""
---
🧩 **Admin Instructions:**  
- To reset and allow a new draw, click the **🔄 Reset for New Round** button (admin only).  
- Or manually delete the file: `winners_record.xlsx` from your app folder or GitHub repo.  
- Update `members_data.xlsx` anytime to refresh the members list.  
- Keep your passcode secure and private.
""")
