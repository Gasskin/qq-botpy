from modules import utils as g_utils
from modules.message_info import MessageInfo
from modules.base_handle import BaseHandle
from modules.resonance import utils as r_utils
from modules.resonance.configs import items
from modules.resonance.configs import city

from modules.resonance.commands.report_buy import BuyInfos

from botpy import logging

import traceback

_log = logging.get_logger()


class SearchBuy(BaseHandle):
    # 商品
    async def HandleMessage(self, m: MessageInfo):
        try:
            item_ids = r_utils.TryFindItemIDs(m.params[0])
            if not item_ids:
                return await r_utils.Reply(m, f"不存在商品：{m.params[0]}")
            content = f"目标商品：{items.Datas[item_ids[0]]['name']}\n"
            for item_id in item_ids:
                content = content + "\n" + self.GetBuyInfoContent(item_id)
            await r_utils.Reply(m, content)
        except Exception as e:
            _log.error(traceback.format_exc())
            await r_utils.Reply(m, "参数错误")

    def GetBuyInfoContent(self, item_id) -> str:
        item = items.Datas[item_id]
        city_name = city.Datas[item["city"]]["name"]
        buy_info = BuyInfos.GetAndAddDefaultIfNone(item_id, item["city"])
        return f"城市：{city_name} 市场：{buy_info.percentage}%{buy_info.GetValid()}"
