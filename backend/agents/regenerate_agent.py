import os
import json
import re
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
import json_repair
from openai import OpenAI
from sqlalchemy.orm import Session
from models import ContentLog

class RegenerateAgent:
    def __init__(self):
        self.model_name = "claude-3-5-sonnet-20241022"

    def regenerate_content(self, db: Session, content_id: int, target_part: str, feedback: str) -> dict:
        log = db.query(ContentLog).filter(ContentLog.id == content_id).first()
        if not log:
            raise ValueError("Content log not found")

        try:
            draft = json_repair.loads(log.content)
        except Exception:
            raise ValueError("Failed to parse existing content")

        # Prepare context based on target
        part_content = ""
        if target_part == "blog":
            part_content = json.dumps(draft.get("blog", {}))
        elif target_part == "linkedin":
            part_content = json.dumps(draft.get("linkedin", {}))
        elif target_part == "x_thread":
            part_content = json.dumps(draft.get("x_thread", {}))
        elif target_part == "newsletter":
            part_content = json.dumps(draft.get("newsletter", {}))
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
   - If newsletter: {{"subject_line": "...", "preview_text": "...", "body": "..."}}
   - If blog_image or linkedin_image: {{"image_prompt": "..."}}
   - If all: return the full structure combining blog, linkedin, x_thread, newsletter.

Zero fluff, no "—" em dashes, and write for a cynical software engineering buyer. 
When writing an image_prompt, ALWAYS write comma-separated keywords (no full sentences), NEVER request text or words in the image, and use visual metaphors over literal tech tropes.
"""

        user_msg = "Please provide the updated JSON for the targeted part."

        try:
            chat = ChatAnthropic(
                model=self.model_name,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                timeout=300.0,
                max_tokens=8192,
                model_kwargs={"extra_headers": {"anthropic-beta": "max-tokens-3-5-sonnet-2024-07-15"}}
            )
            response = chat.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_msg)
            ])
            text = response.content.strip()

            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                updated_part = json_repair.loads(m.group())
            else:
                raise ValueError("Could not parse JSON from Claude's response")

            openai_key = os.getenv("OPENAI_API_KEY", "")
            openai_client = None
            if openai_key.strip():
                try:
                    openai_client = OpenAI(api_key=openai_key)
                except Exception:
                    pass

            if target_part == "blog":
                draft["blog"] = updated_part
                if "image_prompt" in updated_part and updated_part["image_prompt"]:
                    try:
                        if openai_client:
                            img_res = openai_client.images.generate(model="gpt-image-1-mini", prompt=updated_part["image_prompt"], n=1, size="1024x1024")
                            img_data = img_res.data[0]
                            draft["blog"]["image_url"] = f"data:image/png;base64,{img_data.b64_json}" if getattr(img_data, "b64_json", None) else img_data.url
                        else:
                            draft["blog"]["image_url"] = ""
                    except Exception as e:
                        print(f"OpenAI gen failed: {e}")
            elif target_part == "linkedin":
                draft["linkedin"] = updated_part
                if "image_prompt" in updated_part and updated_part["image_prompt"]:
                    try:
                        if openai_client:
                            img_res = openai_client.images.generate(model="gpt-image-1-mini", prompt=updated_part["image_prompt"], n=1, size="1024x1024")
                            img_data = img_res.data[0]
                            draft["linkedin"]["image_url"] = f"data:image/png;base64,{img_data.b64_json}" if getattr(img_data, "b64_json", None) else img_data.url
                        else:
                            draft["linkedin"]["image_url"] = ""
                    except Exception as e:
                        print(f"OpenAI gen failed: {e}")
            elif target_part == "x_thread":
                draft["x_thread"] = updated_part
            elif target_part == "newsletter":
                draft["newsletter"] = updated_part
            elif target_part == "blog_image":
                draft["blog"]["image_prompt"] = updated_part.get("image_prompt", "")
                if draft["blog"]["image_prompt"]:
                    try:
                        if openai_client:
                            img_res = openai_client.images.generate(model="gpt-image-1-mini", prompt=draft["blog"]["image_prompt"], n=1, size="1024x1024")
                            img_data = img_res.data[0]
                            draft["blog"]["image_url"] = f"data:image/png;base64,{img_data.b64_json}" if getattr(img_data, "b64_json", None) else img_data.url
                        else:
                            draft["blog"]["image_url"] = ""
                    except Exception as e:
                        print(f"OpenAI gen failed: {e}")
            elif target_part == "linkedin_image":
                draft["linkedin"]["image_prompt"] = updated_part.get("image_prompt", "")
                if draft["linkedin"]["image_prompt"]:
                    try:
                        if openai_client:
                            img_res = openai_client.images.generate(model="gpt-image-1-mini", prompt=draft["linkedin"]["image_prompt"], n=1, size="1024x1024")
                            img_data = img_res.data[0]
                            draft["linkedin"]["image_url"] = f"data:image/png;base64,{img_data.b64_json}" if getattr(img_data, "b64_json", None) else img_data.url
                        else:
                            draft["linkedin"]["image_url"] = ""
                    except Exception as e:
                        print(f"OpenAI gen failed: {e}")
            elif target_part == "all":
                draft["blog"] = updated_part.get("blog", draft.get("blog"))
                draft["linkedin"] = updated_part.get("linkedin", draft.get("linkedin"))
                draft["x_thread"] = updated_part.get("x_thread", draft.get("x_thread"))
                draft["newsletter"] = updated_part.get("newsletter", draft.get("newsletter"))

            return draft
        except Exception as e:
            raise RuntimeError(f"RegenerateAgent error: {str(e)}")
