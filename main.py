from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Flask app is running."

@app.route("/run", methods=["GET"])
def run_scraper():
    try:
        # Setup headless Chrome
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920x1080")
        driver = webdriver.Chrome(options=options)

        # Visit HK01 Property Market page
        driver.get("https://www.hk01.com/channel/399/地產樓市")
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Extract article links
        article_divs = soup.select("div.content-card--article")
        links = []
        for div in article_divs:
            a_tag = div.find("a", href=True)
            if a_tag:
                href = a_tag["href"]
                full_url = "https://www.hk01.com" + href if href.startswith("/") else href
                links.append(full_url)

        # Loop through article pages
        articles = []
        for url in links:
            try:
                driver.get(url)
                time.sleep(2)
                art_soup = BeautifulSoup(driver.page_source, "html.parser")

                # Title
                title_tag = art_soup.find("h1")
                title = title_tag.get_text(strip=True) if title_tag else ""

                # Date from span with "出版"
                date_text = ""
                for span in art_soup.find_all("span"):
                    if span.get_text(strip=True).startswith("出版"):
                        date_text = span.get_text(strip=True).replace("出版", "").strip()
                        break

                # Photo from og:image
                og_image = art_soup.find("meta", property="og:image")
                photo_url = og_image["content"] if og_image else ""

                # Summary from content
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
                    "date": "",
                    "summary": str(e),
                    "photo_url": "",
                    "link": url
                })

        driver.quit()
        return jsonify({"articles": articles})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
