import streamlit as st
import toml
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from auth import create_users_table, register_user, login_user, delete_user



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


def fetch_reel_data_selenium(url):
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)

    data = {"url": url, "likes": "N/A", "views": "N/A", "caption": "No caption", "thumbnail": ""}
    try:
        spans = driver.find_elements(By.TAG_NAME, "span")
        for span in spans:
            txt = span.text.strip().replace(",", "")
            if txt.lower().endswith("likes"):
                data["likes"] = int(txt.split()[0])
            elif txt.lower().endswith("views"):
                data["views"] = int(txt.split()[0])

        try:
            meta_thumb = driver.find_element(By.XPATH, "//meta[@property='og:image']")
            data["thumbnail"] = meta_thumb.get_attribute("content")
        except:
            pass

        try:
            caption_elem = driver.find_element(By.XPATH, "//div[@role='button']/../div/span")
            data["caption"] = caption_elem.text
        except:
            pass

    except Exception as e:
        st.error(f"Error extracting from {url}: {e}")
    finally:
        driver.quit()
    return data

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
                results.append(fetch_reel_data_selenium(url))

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

