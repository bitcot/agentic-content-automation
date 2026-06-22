from ddgs import DDGS
from openai import OpenAI
import os
from agents.logger import emit_agent_log

class ResearchAgent:
    def __init__(self):
        self.ddgs = DDGS()
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def search_topic(self, query: str, max_results: int = 5) -> str:
        """
        Searches the web for a topic and returns a compiled context string
        of the top results to be injected into an LLM prompt.
        """
        emit_agent_log("ResearchAgent", f"Searching web for: '{query}'", {"query": query})
        try:
            results = list(self.ddgs.text(query, max_results=max_results))
            if not results:
                return "No real-time search results found."

            context = "Here are the top real-time search results to provide factual grounding:\n\n"
            for i, res in enumerate(results):
                context += f"Result {i + 1}:\n"
                context += f"Title: {res.get('title', 'No Title')}\n"
                context += f"Body/Snippet: {res.get('body', 'No snippet')}\n"
                context += f"Source URL: {res.get('href', 'No URL')}\n\n"
            
            return context
        except Exception as e:
            print(f"Web search failed: {e}")
            return f"Web search failed due to an error: {str(e)}"

    def search_image(self, query: str) -> str:
        """
        Searches for web images and uses a Vision model to verify suitability.
        Rejects generic abstract vectors or low quality stock photos.
        """
        emit_agent_log("ResearchAgent", f"Searching for web images matching: '{query}'")
        try:
            # Translate verbose DALL-E prompt into short SEO search query
            try:
                translation_res = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You convert verbose DALL-E image prompts into short, 2-4 word SEO search queries for Google Images. Reply ONLY with the short search query, no quotes, no punctuation."},
                        {"role": "user", "content": query}
                    ],
                    max_tokens=15
                )
                seo_query = translation_res.choices[0].message.content.strip()
                print(f"Translated DALL-E prompt to SEO query: '{seo_query}'")
            except Exception as te:
                print(f"Query translation failed: {te}")
                seo_query = query[:50] # basic fallback
                
            # ENFORCE STRICT SAFESEARCH
            results = list(self.ddgs.images(seo_query, safesearch='strict', max_results=8))
            if not results:
                return ""
            
            for res in results:
                img_url = res.get('image', '')
                if not img_url:
                    continue
                
                try:
                    verification = self.openai_client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text", 
                                        "text": f"You are a strict editorial image reviewer and safety moderator. The topic/context is '{query}'. Evaluate this image. CRITICAL: Immediately reject any image containing NSFW content, nudity, violence, suggestive material, or inappropriate themes. Reject it if it is a generic abstract vector (like floating dots/nodes), irrelevant, or low quality. Reply with exactly YES if it's highly suitable, safe, and specific, or NO if it should be rejected."
                                    },
                                    {
                                        "type": "image_url", 
                                        "image_url": {"url": img_url}
                                    }
                                ]
                            }
                        ],
                        max_tokens=5
                    )
                    verdict = verification.choices[0].message.content.strip().upper()
                    if "YES" in verdict:
                        return img_url
                    else:
                        print(f"Vision rejected image: {img_url}")
                except Exception as e:
                    print(f"Vision eval failed for {img_url}: {e}")
                    continue
            
            # CRITICAL FIX: If ALL web images are rejected by Vision, DO NOT return the first unverified image.
            # Returning "" forces the writer_agent to fallback to DALL-E 3 generation.
            print(f"All {len(results)} web images were rejected by Vision. Falling back to DALL-E generation.")
            return ""
        except Exception as e:
            print(f"Image search failed: {e}")
            return ""
