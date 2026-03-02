import requests
import json
from bs4 import BeautifulSoup
from newspaper import Article
import time

# --- Updated Nepal News Sources ---
NEWS_SOURCES = [
    {
        "newspaper": "Ratopati",
        "base_url": "https://www.ratopati.com"
    },
    {
        "newspaper": "Setopati",
        "base_url": "https://www.setopati.com"
    },
    {
        "newspaper": "The Himalayan Times",
        "base_url": "https://thehimalayantimes.com"
    },
    {
        "newspaper": "eKantipur",
        "base_url": "https://ekantipur.com"
    }
]

# Political Keywords (same meaning)
POLITICAL_KEYWORDS = [
    "election", "vote", "voting", "parliament", "government",
    "prime minister", "minister", "party", "candidate",
    "assembly", "congress", "uml", "maoist", "coalition",
    "ballot", "commission", "poll", "constitutional",
    "HoR", "provincial assembly", "mayor", "chairperson", "ward",
    "constituency", "nc", "maoist centre", "election commission",
    "campaign", "manifesto", "nomination", "proportional representation",
    "first-past-the-post", "polling station", "voter turnout",
    "ballot box", "code of conduct", "cabinet", "reshuffle",
    "government formation", "vote of confidence", "referendum",
    "by-election", "protest", "demonstration", "petition",
    "speaker", "deputy speaker", "mp", "representative"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# Check if article title is political
def is_political(title):
    title = title.lower()
    return any(keyword in title for keyword in POLITICAL_KEYWORDS)

# Extract article content
def extract_article_text(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception:
        return ""

# Simple summarization (first 3 sentences)
def summarize_text(text, max_sentences=3):
    sentences = text.split(". ")
    summary = ". ".join(sentences[:max_sentences])
    return summary.strip() + "."

# Scrape homepage
def scrape_homepage(source):
    articles = []
    try:
        response = requests.get(source["base_url"], headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)

        for link in links:
            title = link.get_text(strip=True)
            url = link["href"]

            if not title or len(title) < 25:
                continue

            if not url.startswith("http"):
                url = source["base_url"] + url

            if is_political(title):
                articles.append({
                    "title": title,
                    "url": url,
                    "source": source["newspaper"]
                })

        return articles[:5]   # limit per source

    except Exception:
        return []

# -------- MAIN PROGRAM --------
results = []

for source in NEWS_SOURCES:
    print(f"Scraping {source['newspaper']}...")
    article_links = scrape_homepage(source)

    for article in article_links:
        text = extract_article_text(article["url"])

        if text.strip():
            summary = summarize_text(text)
            results.append({
                "source": article["source"],
                "title": article["title"],
                "url": article["url"],
                "summary": summary
            })

        time.sleep(2)  # polite delay

# Save to JSON
with open("articles.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print("\nPolitical news summaries saved in articles.json")
