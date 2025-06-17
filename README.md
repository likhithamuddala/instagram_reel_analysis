📊 Instagram Reel Analyzer
This is a Streamlit-based web application that analyzes the performance of Instagram Reels based on the number of likes. It provides insights into how well each reel is performing and includes user authentication using email.

🚀 Features
🔐 Email-based user registration, login, and account deletion

📎 Input multiple Instagram Reel URLs (one per line)

📥 Fetches like counts using Selenium

📈 Generates charts and insights based on like counts

📌 Detects invalid or unsupported URLs

🏆 Highlights the top-performing reel with a summary

🛠️ Tech Stack
Python

Streamlit for UI

Selenium for web scraping

SQLite for user authentication

Pandas for data handling

Chrome WebDriver via webdriver-manager

🔧 Installation
1. Clone the Repository
bash
Copy code
git clone https://github.com/yourusername/instagram-reel-analyzer.git
cd instagram-reel-analyzer
2. Create a Virtual Environment (Optional but recommended)
bash
Copy code
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
3. Install Dependencies
bash
Copy code
pip install -r requirements.txt
▶️ Run the App Locally
bash
Copy code
streamlit run app.py
The app will launch in your browser at http://localhost:8501.

📁 Project Structure
graphql
Copy code
instagram-reel-analyzer/
│
├── app.py              # Main Streamlit app
├── auth.py             # Handles user login/registration
├── users.db            # SQLite database for users
├── requirements.txt    # Required packages
└── README.md           # Project documentation

📌 Notes
Reels are fetched using headless Chrome via Selenium.

Due to Instagram’s privacy policies, only like counts are shown — not views.

You must be logged in to analyze reels.

If Instagram structure changes, scraping logic might need updates.

🧪 Example Reels Format
text

Copy code
https://www.instagram.com/reel/DKZ0YRPzDBz/

https://www.instagram.com/reel/DK9oEIPvECT/

📦 Deployment Options
✅ Deploy on Streamlit Cloud (GUI-based)

✅ Use Render/Railway for Selenium support (Docker recommended)

❌ Streamlit Cloud may not support Selenium on all reels due to Instagram blocking cloud IPs

📬 Contact
Built by Likhitha Muddala
GitHub: github.com/likhithamuddala
