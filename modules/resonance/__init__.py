# 雷索纳斯
from botpy.message import Message
from modules.message_info import MessageInfo
from modules.base_handle import BaseHandle
from modules.resonance.commands.gmr import GMR
from modules.resonance.commands.report_buy import ReportBuy
from modules.resonance.commands.report_sell import ReportSell
from modules.resonance.commands.search_buy import SearchBuy
from modules.resonance.commands.recommend_sell import RecommendSell


class Resonance(object):
    COMMANDS: dict[str, BaseHandle] = {
        "/GMR": GMR(),
        "/ReportBuy": ReportBuy(),
        "/SearchBuy": SearchBuy(),
        "/ReportSell": ReportSell(),
        "/RecommendSell": RecommendSell(),
    }

    def FilterMeesage(self, message_info: MessageInfo) -> bool:
        return message_info.command in self.COMMANDS

    async def HandleMessage(self, message_info: MessageInfo):
        await self.COMMANDS[message_info.command].HandleMessage(message_info)
