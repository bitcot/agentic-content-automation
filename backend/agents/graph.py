from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from agents.icp_agent import ICPAgent
from agents.seo_agent import SEOAgent
from agents.writer_agent import WriterAgent

class ContentState(TypedDict):
    topic: str
    angle: str
    target_persona: str
    tone: str
    author_voice: str
    image_idea: str
    use_web_search: bool
    image_source: str
    db_session: any
    
    # Outputs/Intermediate results
    icp_result: Optional[dict]
    seo_data: Optional[dict]
    draft: Optional[dict]
    status: str  # "success", "reshaped", "rejected"

# Nodes
def icp_node(state: ContentState) -> dict:
    """ICP Score node wrapper."""
    icp_agent = ICPAgent()
    topic = state["topic"]
    angle = state["angle"]
    target_persona = state["target_persona"]
    db = state["db_session"]
    
    icp_result = icp_agent.score_topic(topic, angle=angle, target_persona=target_persona, db=db)
    score = icp_result.get("score", 0.0)
    
    updates = {
        "icp_result": icp_result,
        "status": "success"
    }
    
    if score < 0.65:
        if icp_result.get("reshape_suggestion"):
            # Adopt reshape suggestions
            updates["angle"] = icp_result["reshape_suggestion"]
            updates["status"] = "reshaped"
            # Adjust score in result to pass the pipeline with reshaped state
            icp_result["score"] = 0.65
            icp_result["decision"] = "RESHAPE_ADOPTED"
            updates["icp_result"] = icp_result
        else:
            updates["status"] = "rejected"
            
    return updates

def seo_node(state: ContentState) -> dict:
    """SEO extraction node wrapper."""
    if state["status"] == "rejected":
        return {}
        
    seo_agent = SEOAgent()
    try:
        seo_package = seo_agent.analyze_topic(state["topic"])
        seo_data = seo_package.model_dump() if hasattr(seo_package, 'model_dump') else {}
    except Exception:
        seo_data = {}
        
    return {"seo_data": seo_data}

def writer_node(state: ContentState) -> dict:
    """Writer draft generation node wrapper."""
    if state["status"] == "rejected":
        return {}
        
    writer_agent = WriterAgent()
    draft = writer_agent.generate_draft(
        topic=state["topic"],
        angle=state["angle"],
        icp_result=state["icp_result"],
        target_persona=state["target_persona"],
        tone=state["tone"],
        author_voice=state["author_voice"],
        image_idea=state["image_idea"],
        use_web_search=state["use_web_search"],
        image_source=state["image_source"],
        db=state["db_session"]
    )
    
    return {"draft": draft}

# Conditional Edges
def after_icp_router(state: ContentState) -> str:
    """Routes execution based on the ICP status."""
    if state["status"] == "rejected":
        return "end"
    return "seo"

# Graph Construction
workflow = StateGraph(ContentState)

# Add Nodes
workflow.add_node("icp", icp_node)
workflow.add_node("seo", seo_node)
workflow.add_node("writer", writer_node)

# Set Entry Point
workflow.set_entry_point("icp")

# Add Conditional Edges
workflow.add_conditional_edges(
    "icp",
    after_icp_router,
    {
        "seo": "seo",
        "end": END
    }
)

# Connect linear edges
workflow.add_edge("seo", "writer")
workflow.add_edge("writer", END)

# Compile
app_graph = workflow.compile()
