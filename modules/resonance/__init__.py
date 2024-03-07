# 雷索纳斯
from botpy.message import Message
from modules.message_info import MessageInfo
from modules.base_handle import BaseHandle
from modules.resonance.gmr import GMR


class Resonance(object):
    HANDLES: dict[str, BaseHandle] = {
        "/GMR": GMR(),
        "/Search": 1,
    }

    def FilterMeesage(self, message_info: MessageInfo) -> bool:
        return message_info.command in self.HANDLES

    async def HandleMessage(self, message_info: MessageInfo):
        await self.HANDLES[message_info.command].HandleMessage(message_info)
