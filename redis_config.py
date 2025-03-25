import redis
from config import Config

print(f"Using REDIS_URL: {Config.REDIS_URL}")
cache = redis.Redis.from_url(
    Config.REDIS_URL,
    decode_responses=True
)

redis_client = redis.from_url(
    Config.REDIS_URL,
    decode_responses=True
)
