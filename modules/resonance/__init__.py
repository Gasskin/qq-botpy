# 雷索纳斯
from botpy.message import Message
from modules.message_info import MessageInfo
from modules.base_handle import BaseHandle
from modules.resonance.commands.gmr import GMR
from modules.resonance.commands.report_buy import ReportBuy
from modules.resonance.commands.report_sell import ReportSell
from modules.resonance.commands.search_buy import SearchBuy
from modules.resonance.commands.recommend_sell import RecommendSell
from modules import utils as g_utils
from botpy import logging

_log = logging.get_logger()


class Resonance(object):
    COMMANDS: "dict[str, BaseHandle]" = {
        "/GMR": GMR(),
        "/ReportBuy": ReportBuy(),
        "/SearchBuy": SearchBuy(),
        "/ReportSell": ReportSell(),
        "/RecommendSell": RecommendSell(),
    }

    TIME_LIMIE: "dict[str, float]" = {
        "/GMR": 0,
        "/ReportBuy": 5,
        "/SearchBuy": 5,
        "/ReportSell": 5,
        "/RecommendSell": 10,
    }

    WHITE_ID: dict[str, bool] = {"9631977870258360057": True, "0": False}

    # 玩家ID/指令ID/上一次的发送时间
    SEND_TIME: "dict[str,dict[str,float]]" = {}

    def FilterMeesage(self, message_info: MessageInfo) -> bool:
        return message_info.command in self.COMMANDS

    async def HandleMessage(self, m: MessageInfo):
        # 指令间隔检查
        if m.author_id not in self.WHITE_ID and m.command in self.TIME_LIMIE:
            if m.author_id not in self.SEND_TIME:
                self.SEND_TIME[m.author_id] = {}
            if m.command not in self.SEND_TIME[m.author_id]:
                self.SEND_TIME[m.author_id][m.command] = 0
            last = self.SEND_TIME[m.author_id][m.command]
            now = g_utils.GetCurrentSecondTimeStamp()
            self.SEND_TIME[m.author_id][m.command] = now
            if now - last < self.TIME_LIMIE[m.command]:
                _log.warning(f"{m.author_name} {m.command} 指令发送过于频繁")
                return
        await self.COMMANDS[m.command].HandleMessage(m)
