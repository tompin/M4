import json
from typing import Any, Dict

from channels.generic.websocket import AsyncWebsocketConsumer


class ImageConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        await self.channel_layer.group_add("image_broadcast_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code: int) -> None:
        await self.channel_layer.group_discard("image_broadcast_group", self.channel_name)

    async def image_message(self, event: Dict[str, Any]) -> None:
        # Send image data to WebSocket client
        await self.send(
            text_data=json.dumps(
                {
                    "image_url": event["image_url"],
                }
            )
        )
