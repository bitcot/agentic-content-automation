from pydantic import BaseModel
from typing import Dict

class RepurposedContent(BaseModel):
    linkedin: str
    x_thread: str
    blog: str
    newsletter: str

class RepurposingAgent:
    def __init__(self):
        pass

    def repurpose(self, draft_body: str, title: str, context: dict = None) -> RepurposedContent:
        """
        Takes an approved blog post draft and reformats it for specific platforms.
        Business Rules:
        - Not just copy-pasting, full reformatting for each platform's algorithm.
        - Blog URL never goes in LinkedIn post body (algorithmically suppressed).
        """
        # Placeholder logic
        # In reality, this would use Anthropic API with format-specific prompts
        
        linkedin_post = f"{title}\n\n{draft_body}\n\n[Link in first comment]"
        
        x_thread = f"1/ {title}\n\n{draft_body[:200]}..."
        
        blog_post = f"# {title}\n\n{draft_body}\n\n## Conclusion\nReach out to Bitcot for more info."
        
        newsletter = f"Subject: {title}\n\nHi there,\n\n{draft_body}\n\nBest,\nBitcot Team"

        return RepurposedContent(
            linkedin=linkedin_post,
            x_thread=x_thread,
            blog=blog_post,
            newsletter=newsletter
        )
