import streamlit as st
import sqlite3
import bcrypt

def connect_db():
    return sqlite3.connect("users.db")

def create_users_table():
    conn = connect_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    password TEXT
                )''')
    conn.commit()
    conn.close()

create_users_table()

def register_user(email, password):
    conn = connect_db()
    c = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def validate_user(email, password):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE email = ?", (email,))
    result = c.fetchone()
    conn.close()
    if result and bcrypt.checkpw(password.encode(), result[0]):
        return True
    return False

def delete_user(email):
    conn = connect_db()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE email = ?", (email,))
    conn.commit()
    conn.close()

def show_login_page():
    st.title("🔐 User Authentication")

    tab1, tab2, tab3 = st.tabs(["Login", "Register", "Delete Account"])

    with tab1:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pw")
        if st.button("Login"):
            if validate_user(email, password):
                st.session_state.logged_in = True
                st.success("✅ Logged in successfully!")
            else:
                st.error("❌ Invalid credentials!")

    with tab2:
        st.subheader("Register")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_pw")
        if st.button("Register"):
            if register_user(email, password):
                st.success("✅ Registration successful! Please log in.")
            else:
                st.error("⚠️ Account already exists.")

    with tab3:
        st.subheader("Delete Account")
        email = st.text_input("Email", key="del_email")
        password = st.text_input("Password", type="password", key="del_pw")
        if st.button("Delete Account"):
            if validate_user(email, password):
                delete_user(email)
                st.success("🗑️ Account deleted successfully.")
            else:
                st.error("❌ Invalid credentials.")
