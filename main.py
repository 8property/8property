from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Flask app is running."

@app.route("/run", methods=["GET"])
def run_scraper():
    base_url = "https://www.hk01.com"
    channel_url = f"{base_url}/channel/399/地產樓市"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        resp = requests.get(channel_url, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")

        articles = []
        cards = soup.select("div.content-card--article")[:5]

        for card in cards:
            a_tag = card.find("a", href=True)
            img_tag = card.find("img")
            desc_tag = card.select_one(".content-card__description")

            title = a_tag.get("title") or a_tag.get_text(strip=True) if a_tag else ""
            url = base_url + a_tag["href"] if a_tag else ""
            photo_url = img_tag.get("src") if img_tag else ""
            summary = desc_tag.get_text(strip=True) if desc_tag else ""
            date = datetime.now().strftime("%Y-%m-%d")

            articles.append({
                "title": title,
                "date": date,
                "summary": summary,
                "photo_url": photo_url,
                "link": url
            })

        return jsonify({"articles": articles})

    except Exception as e:
        return jsonify({"error": str(e)})

# ✅ This block ensures Flask runs properly on Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
