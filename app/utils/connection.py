import psycopg2 # type: ignore
import os
import streamlit as st # type: ignore

def get_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            port=os.getenv("POSTGRES_PORT"),
        )
        #st.info("Database connection successful.")
    except psycopg2.Error as e:
        error = f"Error connecting to the database: {e}"
        st.error(error) # Display connection error using streamlit
    return conn


