import requests
import sys

def search_wikimedia(query):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "pageimages",
        "generator": "search",
        "gsrsearch": query,
        "gsrlimit": 1,
        "piprop": "original"
    }
    try:
        r = requests.get(url, params=params, headers={"User-Agent": "Bot"})
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if "original" in page_data:
                return page_data["original"]["source"]
    except Exception as e:
        print("Error:", e)
    return ""

print("Image:", search_wikimedia("LangChain"))
