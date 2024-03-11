from modules import utils as g_utils
from modules.message_info import MessageInfo
from modules.base_handle import BaseHandle
from modules.resonance import utils as r_utils
from modules.resonance.configs import city
import requests
from botpy import logging

import traceback

_log = logging.get_logger()


class SearchSell(BaseHandle):
    # 城市
    async def HandleMessage(self, m: MessageInfo):
        try:
            city_names = r_utils.FindCityNames(m.params[0])
            if city_names == None:
                return await r_utils.Reply(m, "不存在目标城市")
            if len(city_names) > 1:
                return await r_utils.Reply(m, "城市名称存在多个匹配项")
            city_name = city_names[0]
            get = requests.get("https://www.resonance-columba.com/api/get-prices")
            online_products = get.json()["data"]
            content = f"目标城市：{city_name}\n"
            now = g_utils.GetCurrentSecondTimeStamp()
            for product_name in online_products:
                product = online_products[product_name]
                if "sell" not in product:
                    continue
                if city_name not in product["sell"]:
                    continue
                if now - product["sell"][city_name]["time"] >= 3600:
                    continue
                variation = product["sell"][city_name]["variation"]
                trend = "↑" if product["sell"][city_name]["trend"] == "up" else "↓"
                content = content + f"{product_name} {variation} {trend}\n"
            await r_utils.Reply(m, content)
        except:
            _log.error(traceback.format_exc())
            await r_utils.Reply(m, "参数错误")
