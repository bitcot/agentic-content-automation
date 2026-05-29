import os
import json
import re
import urllib.parse
import anthropic
import json_repair
from sqlalchemy.orm import Session
from models import ContentLog

class RegenerateAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def regenerate_content(self, db: Session, content_id: int, target_part: str, feedback: str) -> dict:
        log = db.query(ContentLog).filter(ContentLog.id == content_id).first()
        if not log:
            raise ValueError("Content log not found")

        try:
            draft = json_repair.loads(log.content)
        except Exception:
            raise ValueError("Failed to parse existing content")

        # Prepare context based on target
        # For blog, linkedin, x_thread, blog_image, linkedin_image
        part_content = ""
        if target_part == "blog":
            part_content = json.dumps(draft.get("blog", {}))
        elif target_part == "linkedin":
            part_content = json.dumps(draft.get("linkedin", {}))
        elif target_part == "x_thread":
            part_content = json.dumps(draft.get("x_thread", {}))
        elif target_part == "blog_image":
            part_content = draft.get("blog", {}).get("image_prompt", "")
        elif target_part == "linkedin_image":
            part_content = draft.get("linkedin", {}).get("image_prompt", "")
        else:
            part_content = json.dumps(draft)

        system_prompt = f"""You are an elite Content Strategist and Copywriter for Bitcot.
Your task is to REGENERATE a specific part of an existing draft based on user feedback.

=== ORIGINAL PART CONTENT ===
{part_content}

=== USER FEEDBACK ===
{feedback}

=== INSTRUCTIONS ===
1. Apply the user feedback precisely to the content.
2. Return the updated content strictly in JSON format depending on the target part:
   - If blog: {{"title": "...", "meta_description": "...", "body": "...", "seo_keywords": [...], "internal_links": [...], "word_count": 0, "image_prompt": "..."}}
   - If linkedin: {{"post": "...", "hook_pattern_used": "...", "hashtags": [...], "first_comment": "...", "estimated_engagement": "...", "image_prompt": "..."}}
   - If x_thread: {{"tweets": [...], "dm_keyword": "..."}}
   - If blog_image or linkedin_image: {{"image_prompt": "..."}}
   - If all: return the full structure combining blog, linkedin, x_thread.

Zero fluff, no "—" em dashes, and write for a cynical software engineering buyer. 
When writing an image_prompt, ALWAYS write comma-separated keywords (no full sentences), NEVER request text or words in the image, and use visual metaphors over literal tech tropes.
"""

        user_msg = "Please provide the updated JSON for the targeted part."

        response = self.client.messages.create(
            model="claude-opus-4-7",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_msg}]
        )

        text = response.content[0].text.strip()
        m = re.search(r'\{.*\}', text, re.DOTALL)
        if m:
            updated_part = json_repair.loads(m.group())
        else:
            raise ValueError("Could not parse JSON from Claude's response")

        # Merge updated part back into draft
        if target_part == "blog":
            draft["blog"] = updated_part
            if "image_prompt" in updated_part and updated_part["image_prompt"]:
                encoded = urllib.parse.quote(updated_part["image_prompt"])
                draft["blog"]["image_url"] = f"https://image.pollinations.ai/prompt/{encoded}?width=1200&height=630&nologo=true"
        elif target_part == "linkedin":
            draft["linkedin"] = updated_part
            if "image_prompt" in updated_part and updated_part["image_prompt"]:
                encoded = urllib.parse.quote(updated_part["image_prompt"])
                draft["linkedin"]["image_url"] = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1080&nologo=true"
        elif target_part == "x_thread":
            draft["x_thread"] = updated_part
        elif target_part == "blog_image":
            draft["blog"]["image_prompt"] = updated_part.get("image_prompt", "")
            if draft["blog"]["image_prompt"]:
                encoded = urllib.parse.quote(draft["blog"]["image_prompt"])
                draft["blog"]["image_url"] = f"https://image.pollinations.ai/prompt/{encoded}?width=1200&height=630&nologo=true"
        elif target_part == "linkedin_image":
            draft["linkedin"]["image_prompt"] = updated_part.get("image_prompt", "")
            if draft["linkedin"]["image_prompt"]:
                encoded = urllib.parse.quote(draft["linkedin"]["image_prompt"])
                draft["linkedin"]["image_url"] = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1080&nologo=true"
        elif target_part == "all":
            draft["blog"] = updated_part.get("blog", draft.get("blog"))
            draft["linkedin"] = updated_part.get("linkedin", draft.get("linkedin"))
            draft["x_thread"] = updated_part.get("x_thread", draft.get("x_thread"))

        return draft
