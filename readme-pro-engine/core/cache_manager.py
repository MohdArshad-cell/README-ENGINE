import redis
import json
import os
import hashlib
from dotenv import load_dotenv

load_dotenv()

class CacheManager:
    def __init__(self):
        # Use Upstash or local Redis URL from .env
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client = redis.from_url(self.redis_url, decode_responses=True)
        self.ttl = 86400  # 24 Hours in seconds

    def _get_hash(self, url: str):
        """Generate a unique key for the GitHub URL."""
        return hashlib.md5(url.lower().strip().encode()).hexdigest()

    def get_cached_readme(self, url: str):
        """Check if we already have the AI result for this repo."""
        key = f"readme:{self._get_hash(url)}"
        cached_data = self.client.get(key)
        return json.loads(cached_data) if cached_data else None

    def set_cached_readme(self, url: str, data: dict):
        """Save the result to Redis with a 24-hour expiry."""
        key = f"readme:{self._get_hash(url)}"
        self.client.setex(key, self.ttl, json.dumps(data))
        print(f"🚀 [Cache] Saved result for {url}")

cache_mgr = CacheManager()