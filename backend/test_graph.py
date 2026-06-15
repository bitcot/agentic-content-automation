import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from database import SessionLocal
from agents.graph import app_graph

def run_test():
    db = SessionLocal()
    try:
        initial_state = {
            "topic": "Scaling Kubernetes Control Plane on AWS",
            "angle": "Explain Modular Control Plane scaling trade-offs.",
            "target_persona": "CTO",
            "tone": "thought_leader",
            "author_voice": "bitcot",
            "image_idea": "Diagram of control plane and nodes flow",
            "use_web_search": False,
            "image_source": "ai",
            "db_session": db,
            "icp_result": None,
            "seo_data": None,
            "draft": None,
            "status": ""
        }
        
        print("Invoking LangGraph workflow...")
        final_state = app_graph.invoke(initial_state)
        
        print("\nGraph execution complete.")
        print(f"Status: {final_state['status']}")
        
        icp_res = final_state.get('icp_result')
        if icp_res:
            print(f"ICP Score: {icp_res.get('score')}")
            print(f"ICP Verdict: {icp_res.get('decision')}")
            print(f"ICP Reasoning: {icp_res.get('reasoning')}")
        else:
            print("ICP Result: None")
            
        seo_res = final_state.get('seo_data')
        if seo_res:
            print(f"SEO Keywords: {seo_res.get('target_keyword')}")
        else:
            print("SEO Data: None")
        
        if final_state.get('draft'):
            print("Successfully generated draft!")
            print(f"Blog Title: {final_state['draft'].get('blog', {}).get('h1_title')}")
        else:
            print("No draft generated.")
            
    except Exception as e:
        print(f"Error executing test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_test()
