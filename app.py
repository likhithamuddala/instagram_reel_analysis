import streamlit as st
import pandas as pd
import requests
import re
import toml
from auth import show_login_page

st.set_page_config(page_title="Instagram Reel Analyzer", layout="wide")

def extract_shortcode(url):
    match = re.search(r"instagram\.com/(?:reel|p)/([A-Za-z0-9_-]+)", url)
    return match.group(1) if match else None

@st.cache_resource
def get_instagram_session():
    config = toml.load("config.toml")
    cookies = {
        "sessionid": config["instagram"]["sessionid"],
        "csrftoken": config["instagram"]["csrftoken"],
        "ds_user_id": config["instagram"]["ds_user_id"],
        "mid": config["instagram"]["mid"]
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    session = requests.Session()
    session.headers.update(headers)
    session.cookies.update(cookies)
    return session

def get_reel_likes(shortcode):
    session = get_instagram_session()
    query_url = "https://www.instagram.com/graphql/query/"
    variables = f'{{"shortcode":"{shortcode}"}}'
    params = {
        "query_hash": "d5d763b1e2acf209d62d22d184488e57",
        "variables": variables
    }

    try:
        response = session.get(query_url, params=params)
        if response.status_code == 200:
            json_data = response.json()
            likes = json_data["data"]["shortcode_media"]["edge_media_preview_like"]["count"]
            return likes, None
        else:
            return 0, f"Error {response.status_code}: {response.text}"
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
        return "💡 Good performance — relevant hashtags, appealing visuals, or a semi-viral push."
    elif likes < 90000:
        return "🚀 Strong content — trending audio, good editing, or great timing."
    elif likes < 200000:
        return "🔥 Viral reel — high engagement and visibility, possibly featured in explore."
    elif likes < 500000:
        return "💥 Very viral — massive reach, likely boosted by shares, high retention."
    elif likes < 1000000:
        return "🌍 Explosive reach — global audience impact, possibly cross-platform trending."
    else:
        return "👑 Ultra-viral content — mega influencer or cultural moment."

# Session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    st.title("📊 Instagram Reel Analyzer")

    with st.expander("❓ Why only Likes?"):
        st.markdown("""
        Instagram hides view counts from public APIs. We use only like counts via cookies for safe access.
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
                errors.append(f"Invalid URL: {url}")
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
            top_reel = df.sort_values(by="Likes", ascending=False).iloc[0]
            st.subheader("🔥 Top Performing Reel")
            st.markdown(f"👉 [View Reel]({top_reel['URL']}) — 💖 **{top_reel['Likes']:,} likes**")
            st.markdown(f"📌 **Insight:** {generate_insight(top_reel['Likes'])}")
else:
    show_login_page()
