from modules.message_info import MessageInfo
from modules.base_handle import BaseHandle
from modules import utils as g_utils
from modules.resonance import utils as r_utils
from modules.resonance.configs import items
from modules.resonance.configs import city
from modules.resonance.report_info import ReportInfos

import traceback
from botpy import logging

_log = logging.get_logger()


BuyInfos = ReportInfos()


class ReportBuy(BaseHandle):
    # 商品 价格百分比 城市
    async def HandleMessage(self, m: MessageInfo):
        try:
            percentage = float(m.params[1])
            item_ids = r_utils.TryFindItemIDs(m.params[0])
            if not item_ids:
                return await r_utils.Reply(m, f"不存在商品 {m.params[0]}")
            # 存在多个出售城市
            if isinstance(item_ids, list):
                if len(m.params) < 3:
                    return await r_utils.Reply(m, "商品存在多个出售城市，需要城市参数")
                city_id = r_utils.TryFindCityID(m.params[2])
                if not city_id:
                    return await r_utils.Reply(m, "不存在目标上报城市")
                # 根据所属城市ID，找到真正上报的商品ID
                for item_id in item_ids:
                    if items.Datas[item_id]["city"] == city_id:
                        break
                # 可能没找到
                if items.Datas[item_id]["city"] != city_id:
                    return await r_utils.Reply(
                        m, f"商品 {m.params[0]} 不属于城市 {m.params[2]}"
                    )
            # 只存在唯一出售城市
            else:
                item_id = item_ids
                item = items.Datas[item_id]
                city_id = item["city"]
            BuyInfos.Refresh(
                item_id, city_id, percentage, g_utils.GetCurrentSecondTimeStamp()
            )
            await r_utils.Reply(m, "上报成功")
        except Exception as e:
            _log.error(traceback.format_exc())
            _log.error(e)
            await r_utils.Reply(m, "参数错误")
