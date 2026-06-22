import redis
import json
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# We use a synchronous redis client because the agents run in synchronous threads.
# We will gracefully fail if redis is not available so it doesn't break the agents.
redis_client = None
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    # Test connection
    redis_client.ping()
except Exception as e:
    print(f"Warning: Redis not available for agent logging. {e}")
    redis_client = None

def emit_agent_log(agent_name: str, message: str, data: dict = None):
    """
    Publishes a log message to the 'agent_logs' Redis channel.
    FastAPI will subscribe to this and broadcast to connected WebSockets.
    """
    if not redis_client:
        return
        
    log_event = {
        "type": "AGENT_LOG",
        "agent": agent_name,
        "message": message,
        "data": data or {},
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    try:
        redis_client.publish("agent_logs", json.dumps(log_event))
    except Exception as e:
        print(f"Failed to publish agent log: {e}")
