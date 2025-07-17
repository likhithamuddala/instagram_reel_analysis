import streamlit as st
import toml
import requests
import re
from bs4 import BeautifulSoup
from auth import create_users_table, register_user, login_user, delete_user

# Setup DB and session
create_users_table()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# Performance insight generator
def generate_insight(likes):
    if likes < 100:
        return "🐢 Low visibility — possibly just posted or missing hashtags, reach is very limited."
    elif likes < 1000:
        return "🚧 New or niche content — likely a small follower base or content yet to be discovered."
    elif likes < 10000:
        return "📈 Moderate engagement — might be reaching a specific audience with decent interaction."
    elif likes < 50000:
        return "💡 Good performance — likely due to relevant hashtags, appealing visuals, or a semi-viral push."
    elif likes < 90000:
        return "🚀 Strong content — possibly using trending audio, good editing, or posted at the right time."
    elif likes < 200000:
        return "🔥 Viral reel — high engagement and visibility, possibly featured in explore or trending."
    elif likes < 500000:
        return "💥 Very viral — massive reach, likely boosted by shares, high retention, or celebrity creator."
    elif likes < 1000000:
        return "🌍 Explosive reach — global audience impact, frequently reshared, possibly cross-platform trending."
    else:
        return "👑 Ultra-viral content — mega influencer or cultural moment. This is the top 1% of reels on Instagram."

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
    st.rerun()
if st.sidebar.button("Delete Account"):
    show_delete()
    st.stop()

# Main Page
st.set_page_config(page_title="Instagram Reel Analyzer", layout="centered")
st.title("📊 Instagram Reel Analyzer")
st.write("Paste multiple **Instagram Reel URLs** below (one per line) to analyze performance.")

# Converts likes/views like "1.2K" to 1200
def normalize_count(text):
    if not isinstance(text, str):
        return 0
    text = text.strip().lower().replace(",", "")
    match = re.match(r"([\d\.]+)([km]?)", text)
    if not match:
        return 0
    num, suffix = match.groups()
    num = float(num)
    if suffix == 'k':
        num *= 1_000
    elif suffix == 'm':
        num *= 1_000_000
    return int(num)

# Fetch data from Instagram Reel URL
def fetch_reel_data(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    data = {
        "url": url,
        "likes": "N/A",
        "views": "N/A",
        "caption": "No caption",
        "thumbnail": "",
        "likes_num": 0
    }

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Get thumbnail
        thumb = soup.find("meta", attrs={"property": "og:image"})
        if thumb:
            data["thumbnail"] = thumb["content"]

        # Get caption and fallback likes/views
        cap = soup.find("meta", attrs={"property": "og:description"})
        if cap:
            caption_text = cap["content"]
            data["caption"] = caption_text

            # Extract likes from caption
            like_match = re.search(r"(\d[\d,\.]*[KMkm]?)\s+likes", caption_text)
            if like_match:
                like_val = like_match.group(1)
                data["likes"] = like_val
                data["likes_num"] = normalize_count(like_val)

            # Extract views from caption
            view_match = re.search(r"(\d[\d,\.]*[KMkm]?)\s+views", caption_text)
            if view_match:
                view_val = view_match.group(1)
                data["views"] = view_val

        # Optional span fallback
        spans = soup.find_all("span")
        for span in spans:
            txt = span.text.strip().replace(",", "")
            if txt.lower().endswith("likes") and data["likes"] == "N/A":
                try:
                    count = txt.split()[0]
                    data["likes"] = count
                    data["likes_num"] = normalize_count(count)
                except:
                    pass
            elif txt.lower().endswith("views") and data["views"] == "N/A":
                try:
                    count = txt.split()[0]
                    data["views"] = count
                except:
                    pass

    return data

# Input section
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
            top_reel = max(results, key=lambda r: r["likes_num"])

            st.subheader("🎯 Top Performers")
            st.markdown(f"**By Likes:** ❤️ {top_reel['likes']} — [link]({top_reel['url']})")
            if top_reel["thumbnail"]:
                st.image(top_reel["thumbnail"], width=300)

            insight = generate_insight(top_reel["likes_num"])
            st.markdown(f"🧠 **Insight:** {insight}")

            st.markdown("---")
            st.markdown(f"**By Views:** 👀 {top_reel['views']} — [link]({top_reel['url']})")
            if top_reel["thumbnail"]:
                st.image(top_reel["thumbnail"], width=300)

            insight = generate_insight(top_reel["likes_num"])
            st.markdown(f"🧠 **Insight:** {insight}")

            st.divider()
            st.subheader("📋 All Results")
            for r in results:
                st.markdown(f"**URL**: [link]({r['url']})")
                st.markdown(f"❤️ Likes: {r['likes']} | 👀 Views: {r['views']}")
                st.markdown(f"📝 Caption: {r['caption']}")
                if r["thumbnail"]:
                    st.image(r["thumbnail"], width=250)
                st.markdown("---")
        else:
            st.error("Failed to extract data from any reel.")
