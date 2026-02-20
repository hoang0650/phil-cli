from abc import ABC, abstractmethod
from typing import Dict, Type

class BaseChannel(ABC):
    @abstractmethod
    async def send_message(self, recipient_id: str, text: str):
        pass

    @abstractmethod
    async def receive_message(self, data: dict):
        pass

class TelegramChannel(BaseChannel):
    async def send_message(self, recipient_id: str, text: str):
        print(f"Sending to Telegram {recipient_id}: {text}")
        # Logic gọi API Telegram ở đây

    async def receive_message(self, data: dict):
        print(f"Received from Telegram: {data}")
        return data

class ChannelManager:
    def __init__(self):
        self.channels: Dict[str, BaseChannel] = {
            "telegram": TelegramChannel(),
            # Thêm các kênh khác như discord, whatsapp...
        }

    def get_channel(self, name: str) -> BaseChannel:
        return self.channels.get(name)

    async def route_inbound(self, channel_name: str, data: dict):
        channel = self.get_channel(channel_name)
        if channel:
            return await channel.receive_message(data)
        return None