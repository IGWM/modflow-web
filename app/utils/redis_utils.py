import redis
import json
import os

redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), 
                           port=int(os.getenv('REDIS_PORT', 6379)), 
                           db=0)

def save_simulation_result(simulation_id: str, result: dict):
    redis_client.set(f"simulation:{simulation_id}", json.dumps(result))
    redis_client.set(f"simulation:{simulation_id}:status", "completed")

def get_simulation_status(simulation_id: str):
    status = redis_client.get(f"simulation:{simulation_id}:status")
    return status.decode() if status else "not_found"

def get_simulation_result(simulation_id: str):
    result = redis_client.get(f"simulation:{simulation_id}")
    return json.loads(result) if result else None