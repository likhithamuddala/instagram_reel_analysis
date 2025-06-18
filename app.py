import streamlit as st
import pandas as pd
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from auth import show_login_page

st.set_page_config(page_title="Instagram Reel Analyzer", layout="wide")

def get_chrome_driver():
    options = Options()
    options.binary_location = "/usr/bin/chromium"  # Path for Chromium on Render
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    return webdriver.Chrome(service=Service(), options=options)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    st.title("📊 Instagram Reel Analyzer")

    st.button("🔓 Logout", on_click=lambda: st.session_state.update({'logged_in': False}))

    with st.expander("❓ Why view & like count might not show"):
        st.markdown("""
        Instagram restricts view count access to logged-in users for privacy and platform protection.  
        👉 This tool uses **likes only** to measure reel performance.
        """)

    urls_input = st.text_area("Paste Instagram Reel URLs (one per line):", height=250)
    urls = [url.strip() for url in urls_input.splitlines() if url.strip()]

    def extract_number(text):
        match = re.search(r'([\d.,]+)([kKmM]?)', text)
        if not match:
            return 0
        num = float(match.group(1).replace(',', ''))
        suffix = match.group(2).lower()
        if suffix == 'k':
            num *= 1000
        elif suffix == 'm':
            num *= 1000000
        return int(num)

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

    if st.button("Analyze Reels") and urls:
        st.info("🔍 Fetching reels data... please wait")

        driver = get_chrome_driver()
        data = []

        for url in urls:
            try:
                driver.get(url)
                time.sleep(7)

                source = driver.page_source
                match = re.search(r'([\d.,]+[kKmM]?)\s+likes', source)
                like_count = extract_number(match.group(1)) if match else 0

                data.append({"URL": url, "Likes": like_count})
            except Exception:
                st.error(f"❌ Could not fetch data from: {url}")
                data.append({"URL": url, "Likes": 0})

        driver.quit()

        df = pd.DataFrame(data)
        st.success("✅ Analysis Complete!")
        st.dataframe(df)

        # Bar chart
        st.subheader("📊 Like Count by Reel")
        bar_df = df.copy()
        bar_df['Short URL'] = bar_df['URL'].apply(lambda x: x[:40] + "..." if len(x) > 40 else x)
        st.bar_chart(data=bar_df.set_index('Short URL')['Likes'])

        if not df.empty:
            top = df.loc[df['Likes'].idxmax()]
            st.subheader("🏆 Top Performing Reel")
            st.write(f"🔗 URL: {top['URL']}")
            st.write(f"❤️ Likes: **{top['Likes']}**")
            insight = generate_insight(top['Likes'])
            st.markdown(f"### 💡 Performance Insight\n{insight}")

else:
    show_login_page()
