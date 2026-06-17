import os
import json
import re
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from openai import OpenAI
from sqlalchemy.orm import Session

def load_brand_context(db: Session, keys: list[str]) -> dict:
    """Pull specific keys from brand_context table."""
    from models import BrandContext
    rows = db.query(BrandContext).filter(BrandContext.key.in_(keys)).all()
    return {r.key: r.value for r in rows}

class WriterAgent:
    def __init__(self):
        self.model_name = "claude-opus-4-7"

    def generate_draft(self, topic: str, angle: str = "", icp_result: dict = None, target_persona: str = "", tone: str = "thought_leader", author_voice: str = "bitcot", image_idea: str = "", use_web_search: bool = False, image_source: str = "ai", db: Session = None) -> dict:
        """
        Generate multi-format content (Blog, LinkedIn, X thread) using LangChain ChatAnthropic.
        Loads all voice rules, approved stats, and format rules from memory layer first.
        """
        # Load rich context from memory layer
        ctx = {}
        if db:
            keys_to_load = [
                "voice_rule_8_blog_cta", "voice_rule_9_x_threads", "voice_rule_10_linkedin_url",
                "hook_pattern_a", "hook_pattern_b", "hook_pattern_c", "hook_pattern_d",
                "hook_banned_a", "hook_banned_b", "hook_banned_c",
                "format_linkedin_articles", "format_linkedin_hashtags",
                "format_x_threads", "repost_trigger_pattern",
                "approved_stats_healthcare", "approved_stats_enterprise_ai",
                "approved_stats_digital_transformation", "approved_stats_devops", "approved_stats_ecommerce",
                "seo_service_pages_buried", "seo_internal_link_rule",
                "persona_1_cto", "persona_2_ceo", "persona_3_pm",
                "case_studies", "proof_points",
                "competitor_post_inspiration",
            ]
            
            if author_voice == "raj":
                keys_to_load.extend([
                    "founder_raj",
                    "raj_voice_rule_1_hook", "raj_voice_rule_2_style", "raj_voice_rule_3_themes",
                    "raj_voice_rule_4_storytelling", "raj_voice_rule_5_tech_philosophy",
                    "raj_voice_rule_6_formatting", "raj_voice_rule_7_leadership_lessons",
                    "raj_voice_rule_8_frameworks",
                ])
            else:
                keys_to_load.extend([
                    "founder",
                    "voice_rule_1_hook", "voice_rule_2_brand_mention", "voice_rule_3_paragraphs",
                    "voice_rule_4_h2_endings", "voice_rule_5_real_numbers", "voice_rule_6_tone",
                    "voice_rule_7_banned_words",
                ])

            ctx = load_brand_context(db, keys_to_load)

        persona_match = target_persona if target_persona else icp_result.get("persona_match", "CTO/VP Engineering")

        # Build voice rules block
        if author_voice == "raj":
            founder_profile = ctx.get("founder_raj", "Voice: Raj Sanghvi — Highly inspirational and visionary.")
            voice_rules = "\n".join([
                ctx.get("raj_voice_rule_1_hook", ""),
                ctx.get("raj_voice_rule_2_style", ""),
                ctx.get("raj_voice_rule_3_themes", ""),
                ctx.get("raj_voice_rule_4_storytelling", ""),
                ctx.get("raj_voice_rule_5_tech_philosophy", ""),
                ctx.get("raj_voice_rule_6_formatting", ""),
                ctx.get("raj_voice_rule_7_leadership_lessons", ""),
                ctx.get("raj_voice_rule_8_frameworks", ""),
                ctx.get("voice_rule_8_blog_cta", ""),
                ctx.get("voice_rule_9_x_threads", ""),
                ctx.get("voice_rule_10_linkedin_url", ""),
            ])
        else:
            founder_profile = ctx.get("founder", "Voice: confident, direct, founder who has seen things go wrong many times.")
            voice_rules = "\n".join([
                ctx.get("voice_rule_1_hook", ""),
                ctx.get("voice_rule_2_brand_mention", ""),
                ctx.get("voice_rule_3_paragraphs", ""),
                ctx.get("voice_rule_4_h2_endings", ""),
                ctx.get("voice_rule_5_real_numbers", ""),
                ctx.get("voice_rule_6_tone", ""),
                ctx.get("voice_rule_7_banned_words", ""),
                ctx.get("voice_rule_8_blog_cta", ""),
                ctx.get("voice_rule_9_x_threads", ""),
                ctx.get("voice_rule_10_linkedin_url", ""),
            ])

        # Build hook patterns block
        hook_patterns = "\n".join([
            ctx.get("hook_pattern_a", ""),
            ctx.get("hook_pattern_b", ""),
            ctx.get("hook_pattern_c", ""),
            ctx.get("hook_pattern_d", ""),
        ])

        # Build approved stats block
        approved_stats = "\n".join([
            ctx.get("approved_stats_healthcare", ""),
            ctx.get("approved_stats_enterprise_ai", ""),
            ctx.get("approved_stats_digital_transformation", ""),
            ctx.get("approved_stats_devops", ""),
            ctx.get("approved_stats_ecommerce", ""),
        ])

        # SEO internal linking rule
        seo_rule = ctx.get("seo_internal_link_rule", "")
        buried_pages = ctx.get("seo_service_pages_buried", "")

        # Case studies for reference
        case_studies = ctx.get("case_studies", "")

        # Read playbook
        playbook_path = os.path.join(os.path.dirname(__file__), "content_playbook.txt")
        playbook_content = ""
        if os.path.exists(playbook_path):
            with open(playbook_path, "r", encoding="utf-8") as f:
                playbook_content = f.read()

        image_instruction = ""
        if image_idea:
            image_instruction = f"\n\n═══ USER IMAGE IDEA ═══\nThe user has specifically requested this visual direction for the images: '{image_idea}'. Make sure your generated image_prompt strictly reflects this idea while still obeying the playbook rules.\n"

        research_context = ""
        if use_web_search:
            from agents.research_agent import ResearchAgent
            research_agent = ResearchAgent()
            search_results = research_agent.search_topic(topic)
            research_context = f"\n\n═══ LATEST RESEARCH CONTEXT ═══\nThe user has requested real-time factual grounding for this topic. Use the following real-time facts to ground your content, add specific details, and avoid writing generic statements:\n{search_results}\n"

        ai_learnings = ctx.get("ai_learnings", "")
        learnings_block = f"\n\n═══ AI LEARNINGS (LATEST FEEDBACK LOOP) ═══\nThe following rules have been dynamically extracted from recent performance metrics. These supersede any other rules. You MUST apply these learnings:\n{ai_learnings}\n" if ai_learnings else ""

        system_prompt = f"""You are ghostwriting content for Raj Sanghvi, Founder of Bitcot Technology.
{founder_profile}{image_instruction}{research_context}{learnings_block}
=== CONTENT WRITING FOUNDATIONS PLAYBOOK ===
{playbook_content}

You will produce THREE pieces of content for the same topic: a Blog Post, a LinkedIn Post, and an X Thread.

═══ VOICE RULES — NON-NEGOTIABLE ═══
{voice_rules}

═══ ANTI-JARGON RULES (CRITICAL) ═══
1. NEVER use the em dash (" — ") or the en dash (" – "). This is a dead giveaway for AI-generated text. Use commas, colons, or parentheses instead.
2. ZERO fluff. Do NOT use phrases like "In today's fast-paced digital landscape", "In the rapidly evolving world of", "It's no secret that", or "Navigating the complexities of".
3. Write for cynical software engineering buyers (CTOs, senior developers). If they read this and it sounds like a marketer wrote it, they will bounce. Use direct, unpretentious, sharp language. Focus on systems, trade-offs, architecture, and business outcomes without sugarcoating.

═══ COMPETITOR INSPIRATION (Successful Post Structures to Model) ═══
{ctx.get("competitor_post_inspiration", "")}

═══ WINNING HOOK PATTERNS (use one of these) ═══
{hook_patterns}

═══ BANNED HOOKS (reject and rewrite if you find yourself using these) ═══
{ctx.get("hook_banned_a", "")}
{ctx.get("hook_banned_b", "")}
{ctx.get("hook_banned_c", "")}

═══ APPROVED STATS LIBRARY (use freely — already verified) ═══
{approved_stats}

═══ TARGET PERSONA FOR THIS PIECE ═══
{persona_match}

═══ REAL CASE STUDIES YOU CAN REFERENCE ═══
{case_studies}

═══ SEO INTERNAL LINKING (for blog post only) ═══
{seo_rule}
Service pages to link to: {buried_pages}

═══ HALLUCINATION & STATS RULE ═══
If you use statistics, you MUST either use highly relevant ones from the APPROVED STATS LIBRARY, or if none are relevant, you can use external stats but they MUST be tagged: [NEEDS HUMAN CHECK: describe what to verify]. DO NOT force irrelevant stats (e.g. healthcare stats in a consumer tech post). If no stat perfectly aligns, OMIT IT ENTIRELY.

═══ TRUST SIGNALS & CREDIBILITY (CRITICAL) ═══
You MUST include a strong section establishing credibility. Use exact statements like: "Our team has delivered 100+ mobile applications and worked with enterprise iOS architectures across healthcare, fintech, and SaaS platforms." Do not make claims about the future without grounding them in our past implementation experience.

═══ BLOG BODY STRUCTURE (CRITICAL) ═══
You MUST format the "body" field of the blog exactly as follows to match our proven structure:
1. **Key Takeaways**: Wrapped exactly like this:
<div class="key-takeaways">
  <h2>Key Takeaways</h2>
  <ul>
    <li>Insight 1</li>
    <li>Insight 2</li>
  </ul>
</div>
2. **Table of Contents**: A complete list of all the main topics covered in the blog post, wrapped exactly like this:
<div class="table-of-contents">
  <h2>Table of Contents</h2>
  <ul>
    <li><a href="#introduction">Introduction</a></li>
    <li><a href="#industry-problem">Industry Problem</a></li>
    <!-- List all H2 sections here -->
  </ul>
</div>
3. **Introduction**: Create an urgent hook. Do NOT use generic openings.
3. **Industry Problem**: Describe the friction and broken processes in the industry today.
4. **Strategic Insight / POV**: Our contrarian angle and unique perspective.
5. **What We Built & Tech Stack**: Dive deep into technical architecture.
6. **Challenges and Solutions**: Real-world implementation details.
7. **Business Impact & ROI**: Why executives should care.
8. **Why Bitcot (CTA)**: Establish trust (100+ mobile apps delivered) with a strong conversional CTA.
9. **Conclusion**: A definitive wrap-up wrapping the argument together.
10. **FAQs**: Wrapped exactly like this at the very end:
<div class="faq-section">
  <h2>Frequently Asked Questions</h2>
  <h3>Question 1</h3>
  <p>Answer 1</p>
</div>

Interleave exactly 2 to 3 image placeholders between major paragraphs using this exact format: `[IMAGE: highly detailed prompt for an architectural diagram, cloud architecture data pipeline, or technical flowchart. Avoid generic AI people/robots. Focus on abstract diagrams and workflows.]`

═══ OUTPUT FORMAT ═══
Return ONLY valid JSON with this exact structure:
{{
  "blog": {{
    "title_tag": "< 60 chars, optimized for CTR and keywords",
    "h1_title": "Engaging human-readable title",
    "url_slug": "keyword-dense-hyphenated-slug",
    "meta_description": "...",
    "body": "...",
    "seo_keywords": ["keyword1", "keyword2", "keyword3"],
    "internal_links": ["service page 1", "service page 2"],
    "word_count": <integer>,
    "image_prompt": "highly detailed image generation prompt for the blog header (16:9)",
    "image_alt_text": "Descriptive, keyword-rich alt text for the header image",
    "json_ld_schema": "Raw JSON string for Article schema markup"
  }},
  "linkedin": {{
    "post": "...",
    "hook_pattern_used": "A|B|C|D",
    "hashtags": ["#tag1", "#tag2", "#tag3"],
    "first_comment": "Blog link: https://www.bitcot.com/blog/[slug]",
    "estimated_engagement": "...",
    "image_prompt": "highly detailed image generation prompt for linkedin post graphic (1:1)"
  }},
  "x_thread": {{
    "tweets": ["tweet 1 hook", "tweet 2", "tweet 3", "tweet 4", "tweet 5", "tweet 6 DM hook"],
    "dm_keyword": "KEYWORD_IN_CAPS"
  }},
  "needs_human_check": <true|false>,
  "check_flags": ["list of [NEEDS HUMAN CHECK] items found"]
}}

CRITICAL: Maximum 3 hashtags on LinkedIn. Blog URL never in LinkedIn post body — it goes in first_comment only."""

        if icp_result is None:
            icp_result = {}
            
        user_msg = f"""Topic: {topic}
Angle/Opinion: {angle}
ICP Score: {icp_result.get('score', 0.7):.2f}
Persona: {persona_match}
Tone: {tone}
ICP Reasoning: {icp_result.get('reasoning', '')}

Generate the full Blog + LinkedIn + X Thread now."""

        if use_web_search:
            user_msg += "\n\nCRITICAL INSTRUCTION: You MUST heavily integrate the actual facts, product names, metrics, and details from the WEb Search Context provided above. Do not just write a generic philosophical piece. Ground your contrarian angle strictly in the concrete events/announcements retrieved from the web search."

        try:
            chat = ChatAnthropic(
                model=self.model_name,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                timeout=120.0,
                max_tokens=8192
            )
            response = chat.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_msg)
            ])
            text = response.content.strip()
            
            token_usage = {}
            if hasattr(response, 'response_metadata') and 'usage' in response.response_metadata:
                usage = response.response_metadata['usage']
                inp = usage.get('input_tokens', 0)
                out = usage.get('output_tokens', 0)
                cost = (inp * 0.000015) + (out * 0.000075)
                token_usage = {
                    "input_tokens": inp,
                    "output_tokens": out,
                    "total_tokens": inp + out,
                    "estimated_cost_usd": round(cost, 4)
                }

            # Extract JSON
            import json_repair
            openai_key = os.getenv("OPENAI_API_KEY", "")
            openai_client = None
            if openai_key.strip():
                try:
                    openai_client = OpenAI(api_key=openai_key)
                except Exception:
                    pass

            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                result = json_repair.loads(m.group())
                blog_data = result.get("blog", {})
                blog_body_raw = blog_data.get("body", "")
                
                # Process Inline Images
                def replace_inline_image(match):
                    prompt_text = match.group(1).strip()
                    img_url = ""
                    if image_source == "web":
                        try:
                            from agents.research_agent import ResearchAgent
                            research_agent = ResearchAgent()
                            img_url = research_agent.search_image(prompt_text)
                        except Exception as e:
                            print(f"Web Inline Image search failed: {e}")
                    else:
                        try:
                            if openai_client:
                                img_res = openai_client.images.generate(
                                    model="dall-e-3",
                                    prompt=prompt_text,
                                    n=1,
                                    size="1024x1024",
                                    response_format="b64_json"
                                )
                                img_data_res = img_res.data[0]
                                if hasattr(img_data_res, "b64_json") and img_data_res.b64_json:
                                    img_url = f"data:image/png;base64,{img_data_res.b64_json}"
                                else:
                                    img_url = img_data_res.url
                                if token_usage:
                                    token_usage["estimated_cost_usd"] += 0.040
                        except Exception as e:
                            print(f"OpenAI Inline Image Gen failed: {e}")
                    
                    if img_url:
                        return f"![Architectural Diagram]({img_url})"
                    else:
                        return f"*(Image placeholder: {prompt_text})*"

                if blog_body_raw:
                    blog_data["body"] = re.sub(r'\[IMAGE:\s*(.*?)\]', replace_inline_image, blog_body_raw)

                if "image_prompt" in blog_data and blog_data["image_prompt"]:
                    if image_source == "web":
                        try:
                            from agents.research_agent import ResearchAgent
                            research_agent = ResearchAgent()
                            fetched_url = research_agent.search_image(topic + " " + image_idea)
                            
                            is_valid = False
                            if openai_client and fetched_url:
                                try:
                                    img_check = openai_client.chat.completions.create(
                                        model="gpt-4o-mini",
                                        messages=[
                                            {"role": "user", "content": [
                                                {"type": "text", "text": f"Is this image highly suitable, professional, and relevant for a technical blog post about: {topic}? Reply 'YES' or 'NO'."},
                                                {"type": "image_url", "image_url": {"url": fetched_url}}
                                            ]}
                                        ],
                                        max_tokens=10
                                    )
                                    if "YES" in img_check.choices[0].message.content.upper():
                                        is_valid = True
                                  
                                except Exception as ve:
                                    print(f"Image verification failed: {ve}")
                            
                            if is_valid:
                                blog_data["image_url"] = fetched_url
                            else:
                                print("Web image rejected by AI. Falling back to generation.")
                                raise Exception("Web image rejected.")
                        except Exception as e:
                            blog_data["image_url"] = ""
                            print(f"Web Image search failed: {e}")
                            # Fallback to Generation
                            try:
                                if openai_client:
                                    img_res = openai_client.images.generate(
                                        model="dall-e-3",
                                        prompt=blog_data["image_prompt"],
                                        n=1,
                                        size="1024x1024",
                                        response_format="b64_json"
                                    )
                                    img_data = img_res.data[0]
                                    if hasattr(img_data, "b64_json") and img_data.b64_json:
                                        blog_data["image_url"] = f"data:image/png;base64,{img_data.b64_json}"
                                    else:
                                        blog_data["image_url"] = img_data.url
                                    if token_usage:
                                        token_usage["estimated_cost_usd"] += 0.040
                            except Exception as fall_e:
                                print(f"OpenAI fallback Gen failed: {fall_e}")
                    else:
                        try:
                            if openai_client:
                                img_res = openai_client.images.generate(
                                    model="dall-e-3",
                                    prompt=blog_data["image_prompt"],
                                    n=1,
                                    size="1024x1024",
                                    response_format="b64_json"
                                )
                                img_data = img_res.data[0]
                                if hasattr(img_data, "b64_json") and img_data.b64_json:
                                    blog_data["image_url"] = f"data:image/png;base64,{img_data.b64_json}"
                                else:
                                    blog_data["image_url"] = img_data.url
                                if token_usage:
                                    token_usage["estimated_cost_usd"] += 0.040
                            else:
                                blog_data["image_url"] = ""
                        except Exception as e:
                            blog_data["image_url"] = ""
                            print(f"OpenAI Image Gen failed: {e}")
                
                li_data = result.get("linkedin", {})
                if "image_prompt" in li_data and li_data["image_prompt"]:
                    if image_source == "web":
                        try:
                            from agents.research_agent import ResearchAgent
                            research_agent = ResearchAgent()
                            fetched_url = research_agent.search_image(topic + " " + image_idea)
                            
                            is_valid = False
                            if openai_client and fetched_url:
                                try:
                                    img_check = openai_client.chat.completions.create(
                                        model="gpt-4o-mini",
                                        messages=[
                                            {"role": "user", "content": [
                                                {"type": "text", "text": f"Is this image highly suitable, professional, and relevant for a technical LinkedIn post about: {topic}? Reply 'YES' or 'NO'."},
                                                {"type": "image_url", "image_url": {"url": fetched_url}}
                                            ]}
                                        ],
                                        max_tokens=10
                                    )
                                    if "YES" in img_check.choices[0].message.content.upper():
                                        is_valid = True
                                except Exception as ve:
                                    print(f"Image verification failed: {ve}")
                            
                            if is_valid:
                                li_data["image_url"] = fetched_url
                            else:
                                print("Web image rejected by AI. Falling back to generation.")
                                raise Exception("Web image rejected.")
                        except Exception as e:
                            li_data["image_url"] = ""
                            print(f"Web Image search failed: {e}")
                            # Fallback to Generation
                            try:
                                if openai_client:
                                    img_res = openai_client.images.generate(
                                        model="dall-e-3",
                                        prompt=li_data["image_prompt"],
                                        n=1,
                                        size="1024x1024",
                                        response_format="b64_json"
                                    )
                                    img_data = img_res.data[0]
                                    if hasattr(img_data, "b64_json") and img_data.b64_json:
                                        li_data["image_url"] = f"data:image/png;base64,{img_data.b64_json}"
                                    else:
                                        li_data["image_url"] = img_data.url
                                    if token_usage:
                                        token_usage["estimated_cost_usd"] += 0.040
                            except Exception as fall_e:
                                print(f"OpenAI fallback Gen failed: {fall_e}")
                    else:
                        try:
                            if openai_client:
                                img_res = openai_client.images.generate(
                                    model="dall-e-3",
                                    prompt=li_data["image_prompt"],
                                    n=1,
                                    size="1024x1024",
                                    response_format="b64_json"
                                )
                                img_data = img_res.data[0]
                                if hasattr(img_data, "b64_json") and img_data.b64_json:
                                    li_data["image_url"] = f"data:image/png;base64,{img_data.b64_json}"
                                else:
                                    li_data["image_url"] = img_data.url
                                if token_usage:
                                    token_usage["estimated_cost_usd"] += 0.040
                            else:
                                li_data["image_url"] = ""
                        except Exception as e:
                            li_data["image_url"] = ""
                            print(f"OpenAI Image Gen failed: {e}")

                return {
                    "topic": topic,
                    "icp_score": icp_result.get("score", 0.0),
                    "persona_match": persona_match,
                    "blog": blog_data,
                    "linkedin": li_data,
                    "x_thread": result.get("x_thread", {}),
                    "needs_human_check": result.get("needs_human_check", True),
                    "check_flags": result.get("check_flags", []),
                    "status": "pending_review",
                    "token_usage": token_usage,
                }
            else:
                raise ValueError("No JSON found in Claude response")

        except json.JSONDecodeError as e:
            return {
                "topic": topic,
                "icp_score": icp_result.get("score", 0.0),
                "persona_match": persona_match,
                "blog": {"h1_title": topic, "title_tag": topic, "url_slug": topic.lower().replace(" ", "-"), "body": text, "meta_description": "", "seo_keywords": [], "internal_links": [], "word_count": 0, "image_alt_text": "", "json_ld_schema": ""},
                "linkedin": {"post": "", "hook_pattern_used": "", "hashtags": [], "first_comment": "", "estimated_engagement": ""},
                "x_thread": {"tweets": [], "dm_keyword": ""},
                "needs_human_check": True,
                "check_flags": [f"JSON parse error: {str(e)}"],
                "status": "pending_review",
            }
        except Exception as e:
            raise RuntimeError(f"WriterAgent error: {str(e)}")
