from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Flask app is running."

@app.route("/run", methods=["GET"])
def run_scraper():
    try:
        base_url = "https://www.hk01.com"
        channel_url = f"{base_url}/channel/399/地產樓市"
        headers = {"User-Agent": "Mozilla/5.0"}

        # Get the main page
        resp = requests.get(channel_url, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")

        # Extract up to 5 article links
        links = []
        for card in soup.select("div.content-card--article a[href]"):
            href = card["href"]
            full_url = base_url + href if href.startswith("/") else href
            if full_url not in links:
                links.append(full_url)
            if len(links) >= 5:
                break

        # Scrape each article
        articles = []
        for url in links:
            try:
                res = requests.get(url, headers=headers)
                art_soup = BeautifulSoup(res.text, "html.parser")

                title = art_soup.find("h1").get_text(strip=True) if art_soup.find("h1") else ""

                date_text = ""
                for span in art_soup.find_all("span"):
                    if span.get_text(strip=True).startswith("出版"):
                        date_text = span.get_text(strip=True).replace("出版", "").strip()
                        break

                og_image = art_soup.find("meta", property="og:image")
                photo_url = og_image["content"] if og_image else ""

                paragraphs = art_soup.select("article p")
                full_text = "\n".join([p.get_text(strip=True) for p in paragraphs])
                summary = full_text[:300] + "..." if len(full_text) > 300 else full_text

                articles.append({
                    "title": title,
                    "date": date_text,
                    "summary": summary,
                    "photo_url": photo_url,
                    "link": url
                })

            except Exception as e:
                articles.append({
                    "title": f"Error scraping {url}",
                    "summary": str(e),
                    "link": url,
                    "date": "",
                    "photo_url": ""
                })

        return jsonify({"articles": articles})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
