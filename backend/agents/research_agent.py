from ddgs import DDGS

class ResearchAgent:
    def __init__(self):
        self.ddgs = DDGS()

    def search_topic(self, query: str, max_results: int = 5) -> str:
        """
        Searches the web for a topic and returns a compiled context string
        of the top results to be injected into an LLM prompt.
        """
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
        Searches for a web image and returns the best matching URL.
        """
        try:
            results = list(self.ddgs.images(query, max_results=1))
            if results and len(results) > 0:
                return results[0].get('image', '')
            return ""
        except Exception as e:
            print(f"Image search failed: {e}")
            return ""
