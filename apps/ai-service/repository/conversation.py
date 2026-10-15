import json

from openai.types.responses import ResponseInputParam
from redis.asyncio import Redis
from core.config import settings


class ConversationRepository:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def get(self, conversation_id: str, user_id: str | None) -> ResponseInputParam | None:
        key = "conversation:" + conversation_id
        raw = await self.redis_client.get(key)

        if raw is None:
            return None

        conversation = json.loads(raw)

        if conversation["user_id"] != user_id:
            return None

        return conversation["items"]

    async def save(self, conversation_id: str, user_id: str | None,  items: ResponseInputParam) -> None:
        key = "conversation:" + conversation_id

        await self.redis_client.set(key, json.dumps({
            "user_id": user_id,
            "items": items
        }), ex=settings.conversation_ttl_seconds)




