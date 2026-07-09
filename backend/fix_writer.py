import re
with open("agents/writer_agent.py", "r") as f:
    content = f.read()

# Replace ChatAnthropic with invoke_llm_with_fallback
content = content.replace("from langchain_anthropic import ChatAnthropic", "from agents.llm_utils import invoke_llm_with_fallback")

# Replace ChatAnthropic invocation
old_invoke = """            chat = ChatAnthropic(
                model=self.model_name,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                timeout=120.0,
                max_tokens=8192
            )
            response = chat.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_msg)
            ])"""
new_invoke = """            response = invoke_llm_with_fallback(
                messages=[
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_msg)
                ],
                model=self.model_name,
                max_tokens=8192
            )"""
content = content.replace(old_invoke, new_invoke)

# Change max_tokens and model_name
content = content.replace('self.model_name = "claude-opus-4-7"', 'self.model_name = "claude-3-5-sonnet-20241022"')

# Enforce length
old_body = '"body": The full blog post content in HTML'
new_body = '"body": The comprehensive blog post content in HTML (use <h2>, <h3>, <p>, <ul>, <li>). MUST be at least 1500 words. Dive deep into technical architecture and provide robust analysis.'
content = content.replace(old_body, new_body)

# Fallback image
old_fallback = """                                blog_data["image_url"] = ""
                        except Exception as e:
                            blog_data["image_url"] = ""
                            print(f"OpenAI Image Gen failed: {e}")"""
new_fallback = """                                blog_data["image_url"] = f"https://source.unsplash.com/1024x1024/?{topic.split()[0]},technology"
                        except Exception as e:
                            blog_data["image_url"] = f"https://source.unsplash.com/1024x1024/?{topic.split()[0]},server"
                            print(f"OpenAI Image Gen failed: {e}")"""
content = content.replace(old_fallback, new_fallback)

# json_repair import
content = content.replace("import json_repair", "import json_repair\nimport json")

with open("agents/writer_agent.py", "w") as f:
    f.write(content)
