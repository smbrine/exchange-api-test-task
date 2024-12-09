from app import settings
from utils.redis_wrapper import RedisWrapper

r: RedisWrapper = RedisWrapper(settings.REDIS_ENDPOINT)


async def get_redis():
    return r
