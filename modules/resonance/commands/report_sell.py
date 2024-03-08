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
    # 城市 商品A.百分比A 商品B.百分比B
    async def HandleMessage(self, m: MessageInfo):
        try:
            city_id = r_utils.TryFindCityID(m.params[0])
            if not city_id:
                return await r_utils.Reply(m, f"城市不存在：{m.params[0]}")
            content = ""
            for i in range(1, len(m.params)):
                params = m.params[i].split(".")
                item_ids = r_utils.TryFindItemIDs(params[0])
                if not item_ids:
                    content = content + f"不存在商品：{params[0]}"
                    continue
                percentage = float(params[1])
                if percentage < 80 or percentage > 130:
                    _log.warning(f"{m.author_name} {m.command} 输入百分比异常")
                    continue
                for i in item_ids:
                    SellInfos.Refresh(i, city_id, percentage, g_utils.GetCurrentSecondTimeStamp())
            await r_utils.Reply(m, f"上报成功\n{content}")
        except Exception as e:
            _log.error(traceback.format_exc())
            await r_utils.Reply(m, "参数错误")
