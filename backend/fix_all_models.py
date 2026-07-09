import os
import glob

def fix_models(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    # Fix invalid claude models
    content = content.replace('"claude-opus-4-7"', '"claude-3-5-sonnet-20241022"')
    content = content.replace('"claude-3-opus-20240229"', '"claude-3-5-sonnet-20241022"')

    # Fix image models
    content = content.replace('"gpt-image-1-mini"', '"dall-e-2"')
    content = content.replace('"dall-e-3"', '"dall-e-2"')

    # Make sure length rule is in place for writer_agent.py
    if "writer_agent.py" in filepath:
        old_body = '"body": "...",'
        new_body = '"body": "<CRITICAL: MUST BE AT LEAST 1500 WORDS LONG. Write in deep technical detail. Use HTML. Include EXACTLY 3 [IMAGE: prompt] placeholders interleaving the text. Do NOT output a short summary.>",'
        content = content.replace(old_body, new_body)

    with open(filepath, "w") as f:
        f.write(content)

for filepath in glob.glob("agents/*.py"):
    fix_models(filepath)

print("All models fixed.")
