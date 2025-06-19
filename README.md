# 📊 Instagram Reel Analyzer

A web app that allows users to log in, paste multiple Instagram Reel URLs, and get an analysis of each reel’s likes, views, and caption. It also highlights the top-performing reel based on likes and provides an automated performance **insight**.

## 🌐 Live Demo
[https://instagram-reel-analysis.onrender.com].

---

## 🚀 Features

- 🔐 **User Authentication** (Register, Login, Delete Account)
- 📥 **Paste multiple Instagram Reel URLs**
- 📈 **Analyze Likes and Views** from each reel
- 🏆 **Highlight Top Performer** by Likes
- 🧠 **Insight generator** explains the reason for the top reel's success
- 📝 **View Captions and Thumbnails**
- ☁️ **Deployed on Render**

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: Python, BeautifulSoup, Requests
- **Database**: SQLite (user credentials stored securely)
- **Deployment**: Render.com
- **Auth Module**: Custom lightweight authentication

---

## 🧪 How It Works

1. User logs in or registers
2. User pastes one or more **Instagram Reel URLs** into the text box
3. The app fetches:
   - Reel thumbnail
   - Reel caption
   - Likes and Views (from caption or page content)
4. It highlights the **top reel** by likes, along with an **insight** based on engagement level
5. All reels are shown in a list with their data

---

## 📷 Example Insight

> 💥 Very viral — massive reach, likely boosted by shares, high retention, or celebrity creator.

---

## 🧑‍💻 Local Setup

```bash
git clone https://github.com/likhithamuddala/instagram_reel_analysis.git
cd instagram_reel_analysis
pip install -r requirements.txt
streamlit run app.py
