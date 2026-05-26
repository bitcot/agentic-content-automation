"""
Seed the Supabase Memory Layer with Bitcot's complete brand intelligence.
Run once on setup, re-run quarterly when brand data is updated.
Sources: Developer Reference v1.0, 36-post LinkedIn analysis, GSC data May 2026.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv()

from database import SessionLocal
from models import BrandContext
from datetime import datetime

BRAND_DATA = {

    # ════════════════════════════════════════════════════════════════
    # COMPANY IDENTITY
    # ════════════════════════════════════════════════════════════════
    "company_name": "Bitcot Technology",
    "founded": "2011 — 11+ years in operation",
    "location": "San Diego, California, USA",
    "team_size": "200+ engineers",
    "projects_delivered": "3,000+ projects completed",
    "client_types": "Enterprise, Fortune 500, startups, mid-sized companies",
    "founder": "Raj Sanghvi — voice used for ALL ghostwritten content",
    "positioning": (
        "AI-powered software development agency. Not a vendor — an engineering partner. "
        "Google's #1 reviewed web and mobile app development company in San Diego."
    ),
    "website": "https://www.bitcot.com",
    "contact_phone": "+1 858-683-3692",
    "contact_email": "support@bitcot.com",
    "linkedin_page": "https://www.linkedin.com/company/bitcot",

    # ════════════════════════════════════════════════════════════════
    # FULL SERVICE LIST — all content must connect to at least one
    # ════════════════════════════════════════════════════════════════
    "services_ai": (
        "AI agent development, Workflow automation, GenAI integration, "
        "AI readiness audit, n8n / LangGraph builds."
    ),
    "services_web_mobile": (
        "React / Next.js, React Native, iOS / Android, "
        "Progressive web apps, Custom web apps."
    ),
    "services_healthcare": (
        "Healthcare software, EHR/EMR systems, Telemedicine platforms, "
        "Remote patient monitoring, HIPAA-compliant apps, Wound care software."
    ),
    "services_enterprise": (
        "DevOps transformation, Legacy modernisation, Cloud migration, "
        "Custom software dev, Workflow automation."
    ),
    "services_fintech": (
        "FinTech solutions, Payment integration, Compliance-ready apps."
    ),
    "services_ecommerce": (
        "Custom eCommerce, WooCommerce / Shopify, Headless commerce."
    ),
    "tech_stack": (
        "iOS (Swift), Android, React, Next.js, Node.js, Angular, Java, .NET/C#, AWS. "
        "AI: LangGraph, CrewAI, Phidata, Flowise, Botpress, n8n, Copilot Studio, "
        "Power Automate, AWS Bedrock."
    ),

    # ════════════════════════════════════════════════════════════════
    # VOICE RULES — Raj Sanghvi Ghostwriter Profile
    # Applied on EVERY piece of content
    # ════════════════════════════════════════════════════════════════
    "voice_rule_1_hook": (
        "RULE 1: Always open with a specific stat, reader scenario, contrarian reframe, "
        "or alarming conditional. NEVER with a vague aspiration or product announcement."
    ),
    "voice_rule_2_brand_mention": (
        "RULE 2: Maximum ONE brand mention per content piece. "
        "Only in author bio, closing line, or X thread signature. "
        "NEVER in hook, headline, or body paragraphs."
    ),
    "voice_rule_3_paragraphs": (
        "RULE 3: Short paragraphs — 2 to 3 sentences maximum. "
        "No block of text over 4 sentences."
    ),
    "voice_rule_4_h2_endings": (
        "RULE 4: Every H2 section ends with one actionable, concrete tip. "
        "Not a CTA — an action the reader can take immediately."
    ),
    "voice_rule_5_real_numbers": (
        "RULE 5: Use real numbers wherever possible. "
        "'We've seen this in 40+ builds' is stronger than 'many companies face this'."
    ),
    "voice_rule_6_tone": (
        "RULE 6: Tone: confident, direct, occasionally contrarian. "
        "Not humble. Not promotional. Not corporate. "
        "Writes like a founder who has seen things go wrong many times."
    ),
    "voice_rule_7_banned_words": (
        "RULE 7: BANNED WORDS — never use: leverage, synergy, cutting-edge, "
        "seamless, game-changing, revolutionary, innovative, holistic, transformative journey, "
        "best-in-class, move the needle, digital-first, end-to-end."
    ),
    "voice_rule_8_blog_cta": (
        "RULE 8: End blog posts with ONE soft CTA. "
        "Not 'Contact Bitcot', not 'Get a free quote'. "
        "Example: 'If you're navigating this, drop a comment — happy to share what we've seen.'"
    ),
    "voice_rule_9_x_threads": (
        "RULE 9: X threads: punchy, opinionated, slightly contrarian. "
        "Final tweet has a DM hook keyword in ALL CAPS (e.g. AGENT COST, HEALTHCARE BUILD). "
        "Signature only — no promotion."
    ),
    "voice_rule_10_linkedin_url": (
        "RULE 10: LinkedIn — blog URL always in first comment, NEVER in post body. "
        "LinkedIn's algorithm penalises posts with external links."
    ),

    # ════════════════════════════════════════════════════════════════
    # ICP — THREE PERSONAS
    # ════════════════════════════════════════════════════════════════
    "persona_1_cto": (
        "Persona 1 — CTO / VP Engineering (primary target, highest conversion value). "
        "Titles: CTO, VP Engineering, Head of Engineering, Chief Architect. "
        "Company size: 50–500 employees, mid-market, has budget and team, needs a partner not vendor. "
        "Industries: Healthcare tech, FinTech, SaaS, enterprise software. "
        "Pain points: Technical debt consuming 40%+ of sprints, AI pilot failing in production, "
        "architecture decisions made before scale data existed, security vulnerabilities shipping with features, "
        "legacy system holding back new features. "
        "What they read: Content with specific numbers, real failure scenarios, architecture-level insight. "
        "Skip thought pieces without data. "
        "Hook patterns that work: Pattern A (stat) and Pattern D (alarming conditional). "
        "'Your DevOps pipeline might be shipping vulnerabilities' = 3.39% engagement. "
        "What they share: Content they'd forward to their VP or team. Tool-agnostic, decision-level, NOT tutorial-level."
    ),
    "persona_2_ceo": (
        "Persona 2 — CEO / Founder (high-value, often final decision-maker). "
        "Titles: CEO, Co-founder, Founder, MD, Managing Director. "
        "Company size: 10–200 employees, startup to growth-stage, non-technical or semi-technical. "
        "Pain points: Speed to market, first AI build budget overrun, platform limitations limiting growth, "
        "'good enough' software costing more than custom, not knowing what questions to ask technical partners. "
        "Hook patterns that work: Pattern B (scenario) and Pattern C (reframe). "
        "Business-level framing, not technical. Cost and ROI language. "
        "What they share: Content that validates a decision they're already considering or exposes a risk they hadn't thought about."
    ),
    "persona_3_pm": (
        "Persona 3 — Product Manager (growing influence, often the researcher before CEO decision). "
        "Titles: Product Manager, Senior PM, VP Product, Head of Product. "
        "Pain points: Build vs buy decisions, feature delivery timelines slipping, "
        "user retention after AI feature launch, no visibility into tech debt impact on roadmap. "
        "Hook patterns that work: Practical, checklist-style content. "
        "'Before you commit, ask these 3 questions' format performs well."
    ),
    "icp_geography": (
        "Primary target: United States — California (San Diego, LA, SF, San Jose), Texas, New York. "
        "Deal size: $50K–$500K project engagements. Not freelance, not Fortune 100. Mid-market enterprise. "
        "Buying triggers: Company hit a scaling wall, AI pilot failed, "
        "regulatory pressure (HIPAA, SOC2), competitive pressure to ship AI features, "
        "current agency not delivering."
    ),
    "icp_geo_problem": (
        "CRITICAL: India gets 2,852 clicks vs USA's 1,463. "
        "Content is too generic / listicle-heavy. "
        "Every ICP score MUST penalise topics that attract global informational traffic over US buyer intent traffic. "
        "If India:USA click ratio worsens, ICP scoring weights tighten — only topics with strong US enterprise buyer intent "
        "score above 0.65."
    ),
    "icp_score_threshold": "0.65 — minimum ICP score for any topic to enter the pipeline.",

    # ════════════════════════════════════════════════════════════════
    # COMPETITORS — for Research Agent gap analysis
    # ════════════════════════════════════════════════════════════════
    "competitors_direct": (
        "Direct US/CA competitors: Intellectsoft, Rightpoint, WillowTree, "
        "Cleveroad, Apptunix, Systango, Icreon, Algoworks."
    ),
    "competitors_indirect": (
        "Indirect (larger agencies): Accenture (digital), Deloitte Digital, ThoughtWorks, Capgemini engineering."
    ),
    "competitors_san_diego": (
        "San Diego specific: Bixly, RocketFuel IT, Gorilla Logic, Domo (tools overlap)."
    ),
    "competitor_tracking": (
        "Track per competitor: blog publish frequency, LinkedIn post topics, engagement patterns, "
        "keywords they rank for, what they DON'T cover. Gaps = content opportunities."
    ),
    "competitor_post_inspiration": (
        "Inspiration from high-converting competitor LinkedIn posts: "
        "1. The 'Contrarian Breakdown': Start by calling out a widely accepted industry 'best practice' as wrong. Break down the math/cost. End with how you actually solve it. "
        "2. The 'Autopsy': Detail a failure scenario (e.g., 'A client came to us after blowing $200k on an AI wrapper'). Outline the 3 fatal mistakes made, and the architectural fix required. "
        "3. The 'Framework Drop': Share a proprietary 3-step or 4-step framework for solving a complex engineering problem (e.g., 'How to migrate legacy to cloud without downtime'). Use numbered lists and clear technical terms."
    ),

    # ════════════════════════════════════════════════════════════════
    # EMPIRICALLY VALIDATED CONTENT RULES — 36 post analysis
    # ════════════════════════════════════════════════════════════════
    "hook_pattern_a": (
        "Pattern A — Stat first: Specific number in line 1. "
        "'70% of healthcare AI initiatives fail to scale' — 3.2% avg engagement. "
        "Number MUST be verified and cited. Best for CTO / VP Engineering persona."
    ),
    "hook_pattern_b": (
        "Pattern B — Scenario: Reader's exact situation in line 1. "
        "'We asked a simple question: why are enterprise teams still managing their workforce in spreadsheets?' "
        "— 3.88% CTR (highest of 36 posts). Best for CEO / Founder persona."
    ),
    "hook_pattern_c": (
        "Pattern C — Reframe: 'Your [X] isn't [expected problem], it's [real problem].' "
        "'Your team isn't slow. Your workflows are broken.' — 2.74% engagement + 1 repost. "
        "Best for CEO / Founder and PM personas."
    ),
    "hook_pattern_d": (
        "Pattern D — Alarming conditional: 'What if [bad outcome the reader hasn't thought about]?' "
        "'Is your pipeline shipping vulnerabilities?' — 3.39% engagement, 8 likes. "
        "Best for CTO persona."
    ),
    "hook_banned_a": (
        "BANNED: Vague aspiration — 'Still relying on good enough software?' → 0.54% engagement. "
        "Lowest of 36 posts. Describes every company, resonates with none."
    ),
    "hook_banned_b": (
        "BANNED: Product announcement — 'With the latest innovations in [Tool], businesses can now...' "
        "→ 1.04% engagement. No reader pain addressed."
    ),
    "hook_banned_c": (
        "BANNED: Generic cost warning — 'Are you unknowingly overspending on [X]?' "
        "→ 0.87% engagement. Too broad, no specific scenario."
    ),

    # ════════════════════════════════════════════════════════════════
    # FORMAT RULES BY PLATFORM
    # ════════════════════════════════════════════════════════════════
    "format_linkedin_articles": (
        "LinkedIn articles: best format for ICP-matched healthcare and AI topics. "
        "Avg 627 article views when topic matches ICP. "
        "Use for: architecture, AI failure, scaling, DevOps. "
        "Healthcare AI infra: 631 views, 4.61% engagement."
    ),
    "format_linkedin_image_posts": (
        "LinkedIn image posts: higher engagement rate but lower reach than articles. "
        "ALL 3 reposts came from image posts (not articles). "
        "Best for: sharp insight + bold visual headline. "
        "'Patients trust in 5 seconds' — 3.24% + 3 reposts."
    ),
    "format_linkedin_hashtags": (
        "Hashtag rule: MAXIMUM 3 hashtags per LinkedIn post. "
        "Current posts use 25–35 which SUPPRESSES reach algorithmically. Never more than 3."
    ),
    "format_x_threads": (
        "X thread structure: "
        "Tweet 1 = hook (standalone, irresistible). "
        "Tweets 2–6 = numbered, one insight each. "
        "Tweet 7 = DM hook keyword ALL CAPS. Examples: AGENT COST, HEALTHCARE BUILD."
    ),
    "repost_trigger_pattern": (
        "Content gets reposted when it's shareable to a colleague. "
        "Test: 'Would a CTO forward this to their VP?' If yes — it belongs. "
        "All reposted content was: specific problem + sharp insight + no promotion."
    ),

    # ════════════════════════════════════════════════════════════════
    # TOP-PERFORMING VERTICALS — weight higher in topic scoring
    # ════════════════════════════════════════════════════════════════
    "vertical_healthcare_ai": (
        "Healthcare AI infrastructure: 4.61% engagement, 631 article views. "
        "BEST performing vertical. CTO in healthcare has regulatory pressure + AI mandate + infrastructure gap. "
        "High urgency, high budget. PRIORITISE."
    ),
    "vertical_devops_security": (
        "DevOps / security: 3.39% engagement, 8 likes. Second best. "
        "'Is your pipeline shipping vulnerabilities?' hook works extremely well on engineering leadership."
    ),
    "vertical_digital_transformation": (
        "Digital transformation failure: 2.41–4.06% engagement. "
        "'70% of transformations fail in execution' framing consistently outperforms generic transformation content."
    ),
    "vertical_patient_ux": (
        "Patient-facing healthcare UX: 3 reposts. "
        "'Patients trust in 5 seconds' angle drives resharing. Speaks to healthcare founders directly."
    ),
    "vertical_ai_roi": (
        "AI pilot failure / ROI: 2.2% engagement. "
        "'42% of companies abandoned AI pilots in 2025' — strong stat with commercial intent. "
        "Drives demo requests."
    ),

    # ════════════════════════════════════════════════════════════════
    # PERFORMANCE BASELINES — May 2026
    # ════════════════════════════════════════════════════════════════
    "baseline_linkedin_followers": "16,729",
    "baseline_avg_engagement": "1.82% across 36 posts (Feb–May 2026). Range: 0.54% to 4.61%.",
    "baseline_best_engagement": "4.61% — Healthcare AI infrastructure article, 8 likes, 631 article views",
    "baseline_worst_engagement": "0.54% — 'Still relying on good enough software' — vague hook",
    "baseline_best_ctr": "3.88% — Enterprise workforce portal POC ('We asked why teams still use spreadsheets')",
    "baseline_reposts": "7 reposts total across 36 posts. All from image posts with sharp, colleague-shareable insights.",
    "baseline_newsletter": "5,871 subscribers. 8,089 article views in 3 months. 476 new subscribers in period.",
    "baseline_ga4_visitors": "17,134 unique visitors in 3 months",
    "baseline_form_conversion": (
        "45 form fills in 3 months. 0.26% conversion rate. "
        "1,268 CTA button clicks — 96.4% form abandonment. CRITICAL: fix the form."
    ),
    "baseline_phone_clicks": "548 phone clicks — not tracked as conversions. Add call tracking. High-intent untracked leads.",
    "baseline_usa_organic_ctr": "0.06% USA organic CTR — critically low. Title tags not compelling for US enterprise buyers.",
    "baseline_geo_split": "India: 2,852 clicks vs USA: 1,463 clicks — ICP mismatch.",

    # ════════════════════════════════════════════════════════════════
    # 2x2 CONTENT MATRIX
    # ════════════════════════════════════════════════════════════════
    "matrix_q2_double_down": (
        "Q2 — Double down (high engagement + high conversion): "
        "Healthcare AI infra, Scaling digital health platforms, Enterprise workflow portal, "
        "DevOps security, Telemedicine, eCommerce revenue leaks."
    ),
    "matrix_q1_fix_cta": (
        "Q1 — Fix CTA (high engagement, low conversion): "
        "Healthcare website trust post (3 reposts), Protocol finder, "
        "AI isn't future advantage, Healthcare app chatbot."
    ),
    "matrix_q4_fix_distribution": (
        "Q4 — Fix distribution (low engagement, high conversion): "
        "AI pilot failure article, White-label TCO article, Overspending on product dev."
    ),
    "matrix_q3_rethink": (
        "Q3 — Rethink (low engagement + low conversion): "
        "Good enough software, Modernisation sequencing, Web app bad decisions, "
        "Google AI Studio vibe coding post."
    ),

    # ════════════════════════════════════════════════════════════════
    # SEO INTELLIGENCE — GSC May 2026
    # ════════════════════════════════════════════════════════════════
    "seo_quick_wins": (
        "Quick win pages — positions 7–15, high impressions (title rewrite = fast ranking): "
        "1. 'Best tech stack web apps' — 77,110 impressions, pos 7, 0.03% CTR. "
        "Rewrite: 'Best Tech Stack for Web Apps in 2026: What CTOs Choose and Why'. "
        "2. 'Fastest growing industries' — 75,387 impressions, pos 11, 0.22% CTR. Add year, make tech-specific. "
        "3. 'AI chatbots mental health' — 65,360 impressions, pos 11, 0.25% CTR. ICP-adjacent. "
        "4. 'Best ecommerce websites' — 168,499 impressions, pos 26 — wrong audience, deprioritise."
    ),
    "seo_service_pages_buried": (
        "Revenue pages buried in Google — CRITICAL: "
        "1. AI automation agency — 19,012 impressions, pos 58. Core page. Needs internal links from all AI blog posts. "
        "2. AI development services — 15,765 impressions, pos 65. Every AI blog post must link here. "
        "3. Healthcare mobile app dev — 16,828 impressions, pos 73. LinkedIn healthcare content → drive here. "
        "4. Custom software dev services — 40,327 impressions, pos 71, 0.01% CTR. Title/meta completely uncompelling."
    ),
    "seo_strong_rankings": (
        "Already ranking well (protect and build): "
        "Positions 1–5: Careers (3.6), Vidgrow case study (3.5), Vision framework Swift (2.3), Author bio (4.6). "
        "Positions 6–10: Homepage (6.9), About us (5.4), DevOps infinity loop (10.3), Google Workspace automations (8.0). "
        "New fast-movers: Gemini CLI vs Claude Code (pos 3.6 — moving fast), RAG vs Agentic RAG vs MCP (pos 11.7)."
    ),
    "seo_content_opportunities": (
        "New content opportunities (not yet covered): "
        "AI agents healthcare (pos 49 — huge gap, write now). "
        "RAG vs Agentic RAG vs MCP (pos 11.7 — already moving, accelerate). "
        "Gemini CLI vs Claude Code (pos 3.6 — protect this ranking). "
        "Tech companies CA (pos 20 — build ICP-specific version)."
    ),
    "seo_internal_link_rule": (
        "Internal linking rule: Every new AI blog post MUST link to 'AI automation agency' and 'AI development services' pages. "
        "Every healthcare post MUST link to 'Healthcare mobile app dev' service page. "
        "This is how buried service pages get indexed and ranked."
    ),

    # ════════════════════════════════════════════════════════════════
    # APPROVED STATS LIBRARY — pre-verified, writer can use without check
    # ════════════════════════════════════════════════════════════════
    "approved_stats_healthcare": (
        "VERIFIED — Healthcare stats: "
        "'US physician AI adoption jumped from 38% to 66% in one year, yet 70% of healthcare AI initiatives fail to scale' — Source: multiple industry reports 2025-2026. "
        "'Telehealth market projected to reach $358.96B' — Source: industry analysis. "
        "'Patient digital access grew from 38% to 57%' — Source: ONC data."
    ),
    "approved_stats_enterprise_ai": (
        "VERIFIED — Enterprise AI stats: "
        "'42% of companies abandoned most AI initiatives in 2025, up from 17% in 2024' — Source: industry surveys. "
        "'Only ~5% of AI pilots deliver real revenue impact' — Source: analyst research. "
        "'Technical debt consumes 20–40% of IT budgets' — Source: McKinsey."
    ),
    "approved_stats_digital_transformation": (
        "VERIFIED — Digital transformation stats: "
        "'70% of digital transformations fall short, some studies push failure rate to 88%' — Source: multiple. "
        "'Large tech projects run 45% over budget and deliver 56% less value than expected' — Source: McKinsey + Oxford."
    ),
    "approved_stats_devops": (
        "VERIFIED — DevOps / security stats: "
        "'Average US data breach costs $9.36M' — Source: IBM 2025. "
        "'Organizations adopting DevSecOps deploy 200% faster with fewer incidents' — Source: DORA research. "
        "'Downtime costs $14,056 per minute' — Source: industry benchmarks."
    ),
    "approved_stats_ecommerce": (
        "VERIFIED — eCommerce stats: "
        "'1-second page load delay reduces conversions by up to 7%' — Source: industry benchmark. "
        "'AI-driven personalisation increases average order value by 20–35%' — Source: multiple studies."
    ),

    # ════════════════════════════════════════════════════════════════
    # MEMORY LAYER UPDATE SCHEDULE
    # ════════════════════════════════════════════════════════════════
    "memory_update_schedule": (
        "Every hour: Trigger Agent writes topic scores. "
        "Every publish: Scheduler writes to content_log (topic, hook, platform, ICP score). "
        "Every Monday 8AM: Analytics Agent pulls GA4, LinkedIn, X. Updates performance columns, SEO state, weekly digest. "
        "After each ICP score: Agent writes PASS/RESHAPE/REJECT. Rejected topics blocked for 7 days. "
        "Quarterly: Human updates brand context, competitor list, voice rules, approved stats library."
    ),
    "memory_recalibration_triggers": (
        "Lead converted → topic vertical gets 1.2× weight multiplier. Hook pattern marked 'converted'. "
        "Post reposted → format, hook pattern, vertical flagged as 'high shareability'. "
        "Post engagement < 0.5% → hook pattern flagged 'failed' for this vertical. "
        "Page drops ranking → SEO Agent flags needs_refresh=true. "
        "India:USA ratio worsens → ICP scoring weights tighten."
    ),

    # ════════════════════════════════════════════════════════════════
    # CASE STUDIES
    # ════════════════════════════════════════════════════════════════
    "case_studies": (
        "Kord Fire Protection: AI chatbot integration (at bitcot.com). "
        "Roam MAUI: booking system + custom features for private air shuttle. "
        "Enterprise Health PWA: composable PWA for large health organization. "
        "evrmore: voice-first iOS digital wellness app (in-house product team). "
        "Focus Investment (fintech). Studio SWEAT onDemand (fitness/SaaS). "
        "Reliant Parking (transportation tech). Temocare TeleHealth. JobLog (workforce management)."
    ),
}


def seed():
    db = SessionLocal()
    seeded, updated = 0, 0
    try:
        for key, value in BRAND_DATA.items():
            existing = db.query(BrandContext).filter(BrandContext.key == key).first()
            if existing:
                existing.value = value
                existing.updated_at = datetime.now()
                updated += 1
            else:
                db.add(BrandContext(key=key, value=value))
                seeded += 1
        db.commit()
        print(f"✅ Brand context seeded: {seeded} new, {updated} updated. Total: {seeded + updated} records.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
