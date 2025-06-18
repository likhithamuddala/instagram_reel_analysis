import streamlit as st
import toml
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from auth import create_users_table, register_user, login_user, delete_user
import requests
from bs4 import BeautifulSoup
import json


st.set_page_config(page_title="Instagram Reel Analyzer", layout="centered")
st.title("📊 Instagram Reel Analyzer")
st.write("Paste multiple **Instagram Reel URLs** below (one per line) to analyze performance.")

create_users_table()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""


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

# Show login/register
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


def fetch_reel_data(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
        }
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return {"url": url, "likes": "N/A", "views": "N/A", "caption": "N/A", "thumbnail": "", "error": f"HTTP {response.status_code}"}

        soup = BeautifulSoup(response.text, "html.parser")
        script = soup.find("script", type="application/ld+json")
        if script is None:
            return {"url": url, "likes": "N/A", "views": "N/A", "caption": "N/A", "thumbnail": "", "error": "No metadata found"}

        data = json.loads(script.string)
        return {
            "url": url,
            "likes": data.get("interactionStatistic", {}).get("userInteractionCount", "N/A"),
            "views": "N/A",  # Not available in public metadata
            "caption": data.get("caption", "No caption"),
            "thumbnail": data.get("thumbnailUrl", ""),
        }
    except Exception as e:
        return {"url": url, "likes": "N/A", "views": "N/A", "caption": "N/A", "thumbnail": "", "error": str(e)}

# UI: input multiple URLs
urls_text = st.text_area("📎 Reel URLs (one per line)", height=200)
urls = [u.strip() for u in urls_text.split("\n") if u.strip()]

if st.button("Analyze Reels"):
    if not urls:
        st.warning("Enter at least one reel URL.")
    else:
        results = []
        with st.spinner("Fetching data… this may take time for multiple reels"):
            for url in urls:
                results.append(fetch_reel_data(url))


        if results:
            # Top by likes
            top_likes = max(results, key=lambda r: (isinstance(r["likes"], int), r["likes"]))
            # Top by views
            top_views = max(results, key=lambda r: (isinstance(r["views"], int), r["views"]))

            st.subheader("🎯 Top Performers")
            st.markdown(f"**By Likes:** {top_likes['likes']} ❤ — {top_likes['url']}")
            if top_likes["thumbnail"]: st.image(top_likes["thumbnail"], width=300)
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

