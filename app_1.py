
# ==================== EGSA SHORT TERM LOAN APP ====================

import streamlit as st
import pandas as pd
import mysql.connector
from io import BytesIO

# -------------------- CONFIG --------------------
st.set_page_config(
    page_title="EGSA Short Term Loan App",
    page_icon="📊",
    layout="wide"
)

st.title("📊 EGSA Short Term Loan Management")
st.caption("Live database: TiDB Cloud | lottery_db")

# -------------------- DATABASE CONNECTION --------------------
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        port=int(st.secrets["DB_PORT"]),
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"],
        ssl_ca=st.secrets["DB_CA"],
        ssl_verify_cert=True,
        ssl_verify_identity=True,
        connection_timeout=30
    )

# -------------------- LOAD DATA FROM TIDB --------------------
@st.cache_data(ttl=60)
def load_data():
    conn = get_connection()

    try:
        query = """
            SELECT *
            FROM EGSA2025_short_term_loan
        """

        df = pd.read_sql_query(query, conn)

    finally:
        conn.close()

    return df

# -------------------- REFRESH DATA --------------------
if st.button("🔄 Refresh Database Data"):
    st.cache_data.clear()
    st.rerun()

try:
    with st.spinner("Loading loan records from TiDB Cloud..."):
        df = load_data()

except Exception as e:
    st.error("Unable to connect to TiDB Cloud.")
    st.exception(e)
    st.stop()

st.success("Successfully connected to TiDB Cloud!")

# -------------------- REQUIRED COLUMNS --------------------
required_columns = [
    "loan_id", "business_date", "id", "loan_type",
    "disbursed_amount", "interest_rate", "interest_amount",
    "collection_amount", "from_account", "to_account",
    "due_date", "Phone_no", "status"
]

missing = [c for c in required_columns if c not in df.columns]

if missing:
    st.error(f"Missing database columns: {missing}")
    st.stop()

# -------------------- CLEANING --------------------
valid_types = [
    "level_1", "level_2", "level_3",
    "level_4", "level_5", "level_6"
]

df = df[df["loan_type"].isin(valid_types)].copy()

df["status"] = (
    df["status"]
    .fillna("in progress")
    .astype(str)
    .str.lower()
)

df["due_date"] = pd.to_datetime(
    df["due_date"], errors="coerce"
)

for col in [
    "disbursed_amount",
    "interest_amount",
    "collection_amount"
]:
    df[col] = pd.to_numeric(
        df[col], errors="coerce"
    ).fillna(0)

# -------------------- DAYS CALCULATION --------------------
today = pd.Timestamp.today().normalize()

df["days_left"] = (
    df["due_date"] - today
).dt.days

# -------------------- STATUS LOGIC --------------------
df.loc[
    (df["days_left"] <= 0) &
    (df["collection_amount"] >= df["disbursed_amount"]),
    "status"
] = "completed"

df.loc[
    (df["days_left"] <= 0) &
    (df["collection_amount"] < df["disbursed_amount"]),
    "status"
] = "overdue"

df.loc[df["days_left"] == 1, "status"] = "1 day left"
df.loc[df["days_left"] == 2, "status"] = "2 days left"
df.loc[df["days_left"] > 2, "status"] = "in progress"

# -------------------- FILTERS --------------------
st.sidebar.header("🔍 Filter Loans")

status_options = sorted(df["status"].dropna().unique())

status_filter = st.sidebar.multiselect(
    "Select Status",
    options=status_options,
    default=status_options
)

search_id = st.sidebar.text_input("Search by ID")

filtered_df = df[df["status"].isin(status_filter)].copy()

if search_id:
    filtered_df = filtered_df[
        filtered_df["id"].astype(str).str.contains(
            search_id, case=False, na=False
        )
    ]

# -------------------- GROUPS --------------------
in_progress_df = df[df["status"] == "in progress"]
two_days_df = df[df["status"] == "2 days left"]
one_day_df = df[df["status"] == "1 day left"]
completed_df = df[df["status"] == "completed"]
overdue_df = df[df["status"] == "overdue"]

# -------------------- TOTALS --------------------
def totals(data):
    return (
        data["disbursed_amount"].sum(),
        data["collection_amount"].sum()
    )

in_d, in_c = totals(in_progress_df)
comp_d, comp_c = totals(completed_df)
ov_d, ov_c = totals(overdue_df)

# -------------------- LOAN SUMMARY --------------------
st.subheader("📌 Loan Summary")

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Total Loans", f"{len(df):,}")

col2.metric(
    "In Progress",
    f"{len(in_progress_df):,}",
    f"D: {in_d:,.0f} | C: {in_c:,.0f}"
)

col3.metric("2 Days Left", f"{len(two_days_df):,}")
col4.metric("1 Day Left", f"{len(one_day_df):,}")

col5.metric(
    "Completed",
    f"{len(completed_df):,}",
    f"D: {comp_d:,.0f} | C: {comp_c:,.0f}"
)

col6.metric(
    "Overdue",
    f"{len(overdue_df):,}",
    f"D: {ov_d:,.0f} | C: {ov_c:,.0f}"
)

# -------------------- URGENT LOANS --------------------
st.subheader("⚠️ Urgent Loans (1–2 Days)")

urgent = df[
    df["status"].isin(["1 day left", "2 days left"])
]

if urgent.empty:
    st.success("No urgent loans ✅")
else:
    st.dataframe(
        urgent,
        use_container_width=True,
        hide_index=True
    )

# -------------------- OVERDUE LOANS --------------------
st.subheader("🚨 Overdue Loans")

if overdue_df.empty:
    st.success("No overdue loans ✅")
else:
    st.dataframe(
        overdue_df,
        use_container_width=True,
        hide_index=True
    )

# -------------------- FILTERED LOAN TABLE --------------------
st.subheader("📋 Filtered Loans")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# -------------------- FINANCIAL SUMMARY --------------------
st.subheader("💰 Financial Summary")

total_disbursed = df["disbursed_amount"].sum()
total_interest = df["interest_amount"].sum()
total_collection = df["collection_amount"].sum()

c1, c2, c3 = st.columns(3)

c1.metric("Total Disbursed", f"{total_disbursed:,.2f}")
c2.metric("Total Interest", f"{total_interest:,.2f}")
c3.metric("Total Collection", f"{total_collection:,.2f}")

# -------------------- ADVANCED KPIs --------------------
st.subheader("📊 Advanced KPIs")

recovery_rate = (
    comp_c / comp_d * 100 if comp_d > 0 else 0
)

outstanding = in_d - in_c

active_loans = (
    len(in_progress_df) +
    len(two_days_df) +
    len(one_day_df)
)

k1, k2, k3 = st.columns(3)

k1.metric("Recovery Rate", f"{recovery_rate:.2f}%")
k2.metric("Outstanding Balance", f"{outstanding:,.2f}")
k3.metric("Active Loans", f"{active_loans:,}")

# -------------------- CHARTS --------------------
st.subheader("📈 Status Distribution")

st.bar_chart(
    df["status"].value_counts()
)

st.subheader("💰 Portfolio Distribution")

portfolio = (
    df.groupby("status")["disbursed_amount"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(portfolio)

# -------------------- EXCEL DOWNLOAD --------------------
def to_excel(dataframe):
    output = BytesIO()

    with pd.ExcelWriter(
        output, engine="xlsxwriter"
    ) as writer:
        dataframe.to_excel(
            writer,
            index=False,
            sheet_name="Loans"
        )

    return output.getvalue()

st.subheader("📥 Export Loan Records")

st.download_button(
    "⬇️ Download Updated Excel",
    data=to_excel(filtered_df),
    file_name="EGSA_short_term_loans_updated.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# -------------------- FOOTER --------------------
st.divider()

st.caption(
    "EGSA2025 Short Term Loan Management | "
    "Powered by Streamlit and TiDB Cloud"
)
