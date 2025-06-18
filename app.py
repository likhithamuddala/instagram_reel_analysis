import streamlit as st
import pandas as pd
import instaloader
import re
import os
from auth import show_login_page

st.set_page_config(page_title="Instagram Reel Analyzer", layout="wide")


def extract_shortcode(url):
    """Extract Instagram shortcode from reel URL"""
    match = re.search(r"instagram\.com/(?:reel|p)/([A-Za-z0-9_-]+)", url)
    return match.group(1) if match else None

@st.cache_resource
def get_loader():
    loader = instaloader.Instaloader()
    username = os.getenv("IG_USERNAME")
    password = os.getenv("IG_PASSWORD")
    loader.login(username, password)
    return loader

def get_reel_likes(shortcode):
    """Fetch like count using Instaloader"""
    loader = get_loader()
    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        return post.likes, None
    except Exception as e:
        return 0, str(e)

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

# Session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# MAIN APP
if st.session_state.logged_in:
    st.title("📊 Instagram Reel Analyzer ")

    # Info box explaining why only Likes
    with st.expander("❓ Why view & like count might not show"):
        st.markdown("""
            Instagram restricts view count access to logged-in users for privacy and platform protection. As this tool works without login (for user safety), view counts can't be fetched directly.

            👉 So we rely only on likes to analyze performance.
            """)

    with st.sidebar:
        if st.button("🔓 Logout"):
            st.session_state.logged_in = False
            st.rerun()

    urls_input = st.text_area("Paste Instagram Reel URLs (one per line):", height=250)
    urls = [url.strip() for url in urls_input.splitlines() if url.strip()]

    if st.button("Analyze Reels") and urls:
        data = []
        errors = []

        progress = st.progress(0)
        for i, url in enumerate(urls):
            shortcode = extract_shortcode(url)
            if not shortcode:
                errors.append(f"Invalid URL format: {url}")
                continue

            likes, err = get_reel_likes(shortcode)
            data.append({
                "URL": url,
                "Likes": likes,
                "Status": "Success" if likes > 0 else "Failed"
            })
            if err:
                errors.append(f"{url}: {err}")

            progress.progress((i + 1) / len(urls))

        st.success("✅ Analysis Complete!")
        if errors:
            st.error("Some errors occurred:")
            for e in errors:
                st.write("- " + e)

        df = pd.DataFrame(data)
        st.dataframe(df)

        if not df[df["Likes"] > 0].empty:
            st.bar_chart(df.set_index("URL")["Likes"])

            # 🔥 Top Performing Reel
            top_reel = df.sort_values(by="Likes", ascending=False).iloc[0]
            st.subheader("🔥 Top Performing Reel")
            st.markdown(f"👉 [View Reel]({top_reel['URL']}) — 💖 **{top_reel['Likes']:,} likes**")
            insight = generate_insight(top_reel['Likes'])
            st.markdown(f"📌 **Insight:** {insight}")


else:
    show_login_page()
