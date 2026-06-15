import requests
from bs4 import BeautifulSoup

urls = [
    "https://www.bitcot.com/building-a-smart-ai-powered-reminder-system-in-react-native-with-gemini-local-notifications/",
    "https://www.bitcot.com/interactive-onboarding-flow-in-react-native/",
    "https://www.bitcot.com/voice-to-text-capture-in-react-native-new-architecture-using-expo-speech-recognition/",
    "https://www.bitcot.com/healthcare-development-companies-phi-protection-california/"
]

output = ""

for i, url in enumerate(urls):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.content, 'html.parser')
        
        # Look for main content container
        # Note: on WordPress sites usually it's inside <div class="post-content"> or <article>
        content = soup.find('div', class_='post-content')
        if not content:
            content = soup.find('article')
            
        output += f"\n\n{'='*50}\nBLOG {i+1}: {url}\n{'='*50}\n\n"
        if content:
            # We want to extract some structure, not just flat text.
            for tag in content.find_all(['h2', 'h3', 'p', 'ul']):
                output += tag.get_text(strip=True) + "\n\n"
        else:
            output += "Could not find main content."
    except Exception as e:
        output += f"Error: {e}"

with open('scraped_blogs.txt', 'w') as f:
    f.write(output)

print("Scraping complete.")
