import asyncio
import json
import pickle
import typing as t

from redis import RedisError
import redis.asyncio as aioredis
from redis.asyncio import Redis

from app import config


class RedisWrapper:
    def __init__(
        self,
        redis_url: str,
    ):
        self.r: t.Optional[Redis] = None
        self.r = aioredis.from_url(
            redis_url,
        )

    async def check_connection(self, raise_for_status: bool = False):
        try:
            if not self.r:
                if not raise_for_status:
                    return
                raise RedisError("Redis was not initialized")
            await self.r.ping()
        except RedisError as e:
            self.r = None
            if raise_for_status:
                raise e

    async def get(self, name: str):
        if not self.r or not config.get_config().cache:
            return
        return await self.r.get(name)

    async def set(self, name: str, value, ex, *args, **kwargs):
        if not self.r:
            return
        return await self.r.set(name, value, ex, *args, **kwargs)

    async def hget(
        self,
        name: str,
        key,
        encoding: t.Optional[str] = None,
        fallback: t.Any = None,
    ):
        if not self.r or not config.get_config().cache:
            return
        res = await self.r.hget(name, key)
        if res and encoding:
            res = res.decode(encoding)

        return res or fallback

    async def hset(self, name: str, key, value, *args, ex=0, **kwargs):
        if not self.r:
            return
        await self.r.hset(name, key, value, *args, **kwargs)
        if ex:
            await self.r.expire(name, ex)

    async def hdel(self, name: str, key):
        if not self.r:
            return
        await self.r.hdel(name, key)

    async def hsetbatch(
        self,
        name: str,
        batch: t.Dict[str, t.Any],
        *args,
        ex: int = 0,
        wrong_type_behavior: t.Literal[
            "raise", "str", "bytes", "drop"
        ] = "raise",
        **kwargs,
    ):
        if not self.r:
            return

        def handle_value(val):
            if val is None or isinstance(val, (str, bytes, int, float)):
                return val

            match wrong_type_behavior:
                case "raise":
                    raise TypeError(
                        f"Unsupported type for Redis: {type(val)}"
                    )
                case "str":
                    if isinstance(val, (list, dict)):
                        return json.dumps(val)
                    return str(val)
                case "bytes":
                    return pickle.dumps(val)
                case "drop":
                    return None

        tasks = []

        for k, v in batch.items():
            if v is None:
                tasks.append(self.hdel(name, k))
                continue

            processed_value = handle_value(v)
            if processed_value is not None:
                tasks.append(
                    self.hset(
                        name, k, processed_value, ex=ex, *args, **kwargs
                    )
                )

        await asyncio.gather(*tasks)

    async def hgetall(self, name: str, encoding=None):
        if not self.r or not config.get_config().cache:
            return
        raw_res = await self.r.hgetall(name)
        if not raw_res or not encoding:
            return raw_res
        res = {}
        for raw_k, raw_v in raw_res.items():
            v = raw_v.decode(encoding)
            try:
                v = json.loads(v)
            except json.JSONDecodeError:
                pass
            res[raw_k.decode(encoding)] = v
        return res

    async def hmget(
        self,
        name: str,
        keys: t.List[str],
        encoding: t.Optional[str] = None,
    ):
        if not self.r or not config.get_config().cache:
            return
        raw_res = await self.r.hmget(name, keys=keys)

        res = [
            e.decode(encoding) if e is not None and encoding else e
            for e in raw_res
        ]

        return res

    async def keys(self, pattern: str):
        if not self.r or not config.get_config().cache:
            return
        return await self.r.keys(pattern)
