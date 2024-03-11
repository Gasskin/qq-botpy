from modules import utils as g_utils
from modules.message_info import MessageInfo
from modules.base_handle import BaseHandle
from modules.resonance import utils as r_utils
from modules.resonance.report_info import ReportInfos
from modules.resonance.configs.city import Datas as CityData
from modules.resonance.configs.items import Datas as ItemData
from botpy import logging

import traceback

_log = logging.get_logger()

SellInfos = ReportInfos()


class ReportSell(BaseHandle):
    # 城市 商品A.商品B... 价格A.价格B...
    # 如果商品名称以*结尾，说明要全名匹配
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
                item = items[i]
                if item.endswith("*"):
                    name = item.replace("*", "")
                    item_ids = r_utils.FindItemIDsByFullSearch(name)
                else:
                    item_ids = r_utils.FindItemIDs(item)
                if not item_ids:
                    content = content + f"不存在商品：{item}"
                    continue
                if not r_utils.CheckItemAllSame(item_ids):
                    content = content + f"{item} 存在多个匹配项\n"
                    continue
                percentage = float(price[i])
                if percentage < 80 or percentage > 130:
                    _log.warning(f"{m.author_name} {m.command} 输入百分比异常")
                    continue
                for j in item_ids:
                    SellInfos.Refresh(j, city_id, percentage, g_utils.GetCurrentSecondTimeStamp())
            await r_utils.Reply(m, f"上报成功\n跳过的异常项：\n{content}")
        except Exception as e:
            _log.error(traceback.format_exc())
            await r_utils.Reply(m, "参数错误")
