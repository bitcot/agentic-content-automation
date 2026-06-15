import requests
from bs4 import BeautifulSoup
import json

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
        content = soup.find('div', class_='post-content') or soup.find('article') or soup.find('main')
        
        output += f"\n\n{'='*50}\nBLOG {i+1}: {url}\n{'='*50}\n\n"
        if content:
            output += content.get_text(separator='\n', strip=True)
        else:
            output += "Could not find main content."
    except Exception as e:
        output += f"Error: {e}"

with open('scraped_blogs.txt', 'w') as f:
    f.write(output)

print("Scraping complete.")
