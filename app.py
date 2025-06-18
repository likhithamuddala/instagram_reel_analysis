import streamlit as st
import re
import toml
import requests
from bs4 import BeautifulSoup
from auth import create_users_table, register_user, login_user, delete_user

# Setup DB and session
create_users_table()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# Auth UI
def show_login():
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login_user(username, password):
            st.success("Logged in!")
            st.session_state.logged_in = True
            st.session_state.username = username
        else:
            st.error("Invalid username or password")

def show_register():
    st.subheader("📝 Register")
    username = st.text_input("New Username")
    email = st.text_input("Email (optional)")
    password = st.text_input("New Password", type="password")
    if st.button("Register"):
        if register_user(username, password, email):
            st.success("Registered! Please log in.")
        else:
            st.error("Username already exists.")

def show_delete():
    st.subheader("⚠️ Delete Account")
    if st.button("Delete My Account"):
        delete_user(st.session_state.username)
        st.success("Account deleted.")
        st.session_state.logged_in = False
        st.session_state.username = ""

# Auth Logic
if not st.session_state.logged_in:
    option = st.radio("Select", ["Login", "Register"])
    if option == "Login":
        show_login()
    else:
        show_register()
    st.stop()

st.sidebar.success(f"👤 Logged in as: {st.session_state.username}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.experimental_rerun()
if st.sidebar.button("Delete Account"):
    show_delete()
    st.stop()

# MAIN UI
st.set_page_config(page_title="Instagram Reel Analyzer", layout="centered")
st.title("📊 Instagram Reel Analyzer")
st.write("Paste multiple **Instagram Reel URLs** below (one per line) to analyze performance.")

def fetch_reel_data(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract the caption text from the page
        caption_tag = soup.find("meta", property="og:description")
        caption = caption_tag["content"] if caption_tag else "No caption found"

        # Extract video URL (for embedding in results)
        video_tag = soup.find("meta", property="og:video")
        video_url = video_tag["content"] if video_tag else None

        # Extract likes from caption using regex
        likes_match = re.search(r'(\d[\d.,KkMm]*?) likes', caption)
        likes = likes_match.group(1) if likes_match else "N/A"

        # Extract views (if possible, currently hard to get reliably without API/Selenium)
        views = "N/A"

        return {
            "url": url,
            "likes": likes,
            "views": views,
            "caption": caption,
            "video_url": video_url,
        }

    except Exception as e:
        return {
            "url": url,
            "likes": "Error",
            "views": "Error",
            "caption": f"Error fetching data: {str(e)}",
            "video_url": None,
        }

# UI: input multiple URLs
urls_text = st.text_area("📎 Reel URLs (one per line)", height=200)
urls = [u.strip() for u in urls_text.split("\n") if u.strip()]

if st.button("Analyze Reels"):
    if not urls:
        st.warning("Enter at least one reel URL.")
    else:
        results = []
        with st.spinner("Fetching data…"):
            for url in urls:
                results.append(fetch_reel_data(url))

        if results:
            top_likes = max(results, key=lambda r: (isinstance(r["likes"], int), r["likes"]))
            top_views = max(results, key=lambda r: (isinstance(r["views"], int), r["views"]))

            st.subheader("🎯 Top Performers")
            st.markdown(f"**By Likes:** {top_likes['likes']} ❤ — {top_likes['url']}")
            if "thumbnail" in top_likes and top_likes["thumbnail"]:st.image(top_likes["thumbnail"], width=300)
            st.markdown("---")
            st.markdown(f"**By Views:** {top_views['views']} 👀 — {top_views['url']}")
            if top_views["thumbnail"]: st.image(top_views["thumbnail"], width=300)

            st.divider()
            st.subheader("📋 All Results")
            for r in results:
                st.markdown(f"**URL**: {r['url']}")
                st.markdown(f"❤️ Likes: {r['likes']} | 👀 Views: {r['views']}")
                st.markdown(f"📝 Caption: {r['caption']}")
                if r["thumbnail"]: st.image(r["thumbnail"], width=250)
                st.markdown("---")
        else:
            st.error("Failed to extract data from any reel.")
