import streamlit as st
import snowflake.connector
import pandas as pd

st.title("Melanie's Snowflake Smoothies")

# Connect to Snowflake using secrets
conn = snowflake.connector.connect(
    user=st.secrets["SNOWFLAKE_USER"],
    password=st.secrets["SNOWFLAKE_PASSWORD"],
    account=st.secrets["SNOWFLAKE_ACCOUNT"],
    warehouse=st.secrets["SNOWFLAKE_WAREHOUSE"],
    database=st.secrets["SNOWFLAKE_DATABASE"],
    schema=st.secrets["SNOWFLAKE_SCHEMA"],
)

# Example query to test connection
query = "SELECT CURRENT_VERSION()"

cur = conn.cursor()
cur.execute(query)
result = cur.fetchone()

st.write(f"Connected to Snowflake version: {result[0]}")

cur.close()
conn.close()
