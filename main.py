from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Replit Flask app is running."

@app.route("/run", methods=["GET"])
def run_scraper():
    base_url = "https://www.hk01.com"
    channel_url = f"{base_url}/channel/399/地產樓市"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(channel_url, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")

        article_cards = soup.select("div.content-card--article")
        articles = []

        for card in article_cards[:5]:  # limit to first 5 articles
            a_tag = card.find("a", href=True)
            img_tag = card.find("img")
            title_tag = card.select_one(".content-card__title")
            date_tag = card.select_one(".meta-block__publish-date")

            url = base_url + a_tag["href"] if a_tag else ""
            photo_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else ""
            title = title_tag.text.strip() if title_tag else ""
            date = date_tag.text.strip() if date_tag else ""
            summary = ""

            articles.append({
                "title": title,
                "date": date,
                "summary": summary,
                "photo_url": photo_url,
                "link": url
            })

        return jsonify({"articles": articles})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
