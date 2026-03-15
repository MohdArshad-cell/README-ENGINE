import redis
import os
import hashlib
import json

class CacheManager:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL")
        self.client = None
        
        # Check if URL exists and has the correct scheme
        if self.redis_url and (self.redis_url.startswith("redis://") or self.redis_url.startswith("rediss://")):
            try:
                self.client = redis.from_url(self.redis_url, decode_responses=True)
                # Test connection
                self.client.ping()
                print("✅ [Cache] Connected to Redis successfully.")
            except Exception as e:
                print(f"⚠️ [Cache] Redis connection failed: {e}. Caching disabled.")
                self.client = None
        else:
            print("⚠️ [Cache] REDIS_URL is missing or invalid. Caching disabled.")

    def get_cached_readme(self, url):
        if not self.client: return None
        try:
            key = f"readme:{hashlib.md5(url.encode()).hexdigest()}"
            data = self.client.get(key)
            return json.loads(data) if data else None
        except:
            return None

    def set_cached_readme(self, url, data):
        if not self.client: return
        try:
            key = f"readme:{hashlib.md5(url.encode()).hexdigest()}"
            self.client.setex(key, 86400, json.dumps(data))
        except Exception as e:
            print(f"❌ [Cache] Save error: {e}")

cache_mgr = CacheManager()