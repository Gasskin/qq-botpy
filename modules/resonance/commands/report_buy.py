from modules.message_info import MessageInfo
from modules.base_handle import BaseHandle
from modules import utils as g_utils
from modules.resonance import utils as r_utils
from modules.resonance.configs.city import Datas as CityData
from modules.resonance.configs.items import Datas as ItemData
from modules.resonance.report_info import ReportInfos

import traceback
from botpy import logging

_log = logging.get_logger()

BuyInfos = ReportInfos()


class ReportBuy(BaseHandle):
    # 城市 商品A.商品B... 价格A.价格B...
    async def HandleMessage(self, m: MessageInfo):
        try:
            city_ids = r_utils.TryFindCityIDs(m.params[0])
            if not city_ids:
                return await r_utils.Reply(m, f"城市不存在：{m.params[0]}")
            if len(city_ids) > 1:
                return await r_utils.Reply(m, f"{m.params[0]} 存在多个匹配项")
            city_id = city_ids[0]
            content = ""
            items = m.params[1].split(".")
            price = m.params[2].split(".")
            for i in range(0, len(items)):
                item_id = r_utils.FindOnlyItemWithCityID(items[i], city_id)
                if not item_id:
                    content = content + f"城市{m.params[0]} 不存在商品：{items[i]}\n"
                    continue
                percentage = float(price[i])
                if percentage < 80 or percentage > 130:
                    _log.warning(f"{m.author_name} {m.command} 输入百分比异常")
                    continue
                BuyInfos.Refresh(item_id, city_id, percentage, g_utils.GetCurrentSecondTimeStamp())
            await r_utils.Reply(m, f"上报成功\n跳过的异常项：{content}")
        except Exception as e:
            _log.error(traceback.format_exc())
            await r_utils.Reply(m, "参数错误")
