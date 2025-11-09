import redis
from app.config import settings
import json
from typing import Optional, Any

class RedisClient:
    def __init__(self):
        self.redis = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
    
    def get(self, key: str) -> Optional[Any]:
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis GET error: {e}")
            return None
        
    def set(self, key: str, value: Any, ttl: int = 3600):
        try:
            self.redis.setex(
                key, 
                ttl,
                json.dumps(value)
            )
            return True
        except Exception as e:
            print(f"Redis SET error: {e}")
            return False
    
    def delete(self, key: str):
        try: 
            self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Redis DELETE error: {e}")
            return False
        
    def flush_all(self):
        try:
            self.redis.flushall()
            return True
        except Exception:
            print(f"Redis FLUSHALL error: {Exception}")
            return False

redis_client = RedisClient()