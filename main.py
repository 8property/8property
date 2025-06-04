from flask import Flask
import requests
from bs4 import BeautifulSoup

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
        links = []
        for card in article_cards:
            a_tag = card.find("a", href=True)
            if a_tag:
                href = a_tag["href"]
                full_url = base_url + href if href.startswith("/") else href
                links.append(full_url)

        results = []
        for url in links[:3]:  # limit to 3 for testing
            try:
                article_resp = requests.get(url, headers=headers)
                article_soup = BeautifulSoup(article_resp.text, "html.parser")

                title_tag = article_soup.find("h1")
                title = title_tag.get_text(strip=True) if title_tag else ""

                date = ""
                for span in article_soup.find_all("span"):
                    if "出版" in span.get_text():
                        date = span.get_text(strip=True).replace("出版", "").strip()
                        break

                paragraphs = article_soup.select("article p")
                full_text = "\n".join([p.get_text(strip=True) for p in paragraphs])
                summary = full_text[:300] + "..." if len(full_text) > 300 else full_text

                og_image = article_soup.find("meta", property="og:image")
                photo_url = og_image["content"] if og_image else ""

                payload = {
                    "title": title,
                    "date": date,
                    "summary": summary,
                    "photo_url": photo_url,
                    "link": url
                }

                print("🔍 Scraped:", payload)
                results.append(payload)

            except Exception as e:
                print(f"❌ Error scraping {url}: {e}")

        # Send to Make.com Webhook
        for article in results:
            try:
                webhook_url = "https://hook.us1.make.com/YOUR_WEBHOOK_HERE"  # Replace with your actual webhook
                print(f"📤 Sending to Make.com: {article['title']}")
                r = requests.post(webhook_url, json=article)
                print(f"➡️  Response status: {r.status_code}, text: {r.text}")
            except Exception as e:
                print(f"❌ Failed to send article: {e}")

        return "✅ Scraper ran and data sent.", 200

    except Exception as e:
        return f"❌ Scraper error: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
