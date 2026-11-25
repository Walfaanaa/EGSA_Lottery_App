
import streamlit as st
import pandas as pd
import mysql.connector

st.set_page_config(
    page_title="EGSA2025 Loan Dashboard",
    layout="wide"
)

st.title("EGSA2025 Short Term Loan Dashboard")

def get_connection():
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        port=int(st.secrets["DB_PORT"]),
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"],
        ssl_verify_cert=True,
        ssl_verify_identity=True
    )

try:
    conn = get_connection()

    query = """
        SELECT *
        FROM EGSA2025_short_term_loan
    """

    df = pd.read_sql(query, conn)
    conn.close()

    st.success("Connected to TiDB Cloud!")

    st.metric("Total Records", f"{len(df):,}")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

except Exception as e:
    st.error(f"Database connection failed: {e}")
