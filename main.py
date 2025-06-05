from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime

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
        for card in article_cards[:5]:  # Limit to 5 articles
            a_tag = card.find("a", href=True)
            title_tag = card.select_one("div.content-card__title > span")
            image_tag = card.find("img", src=True)

            if not a_tag or not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            url = base_url + a_tag["href"]
            date = datetime.today().strftime('%Y-%m-%d')
            summary = "No summary"
            photo_url = image_tag["src"] if image_tag else ""

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

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
