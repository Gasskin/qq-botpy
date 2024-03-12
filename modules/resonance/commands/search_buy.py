from modules import utils as g_utils
from modules.message_info import MessageInfo
from modules.base_handle import BaseHandle
from modules.resonance import utils as r_utils
from modules.resonance.configs import city
import requests
from botpy import logging

import traceback

_log = logging.get_logger()


class SearchBuy(BaseHandle):
    # 已经通报过的数据
    already_report: dict[str, str] = {}

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
                if "buy" not in product:
                    continue
                if city_name not in product["buy"]:
                    continue
                if now - product["buy"][city_name]["time"] >= 3600:
                    continue
                variation = product["buy"][city_name]["variation"]
                trend = "↑" if product["buy"][city_name]["trend"] == "up" else "↓"
                content = content + f"{product_name} {variation} {trend}\n"
            await r_utils.Reply(m, content)
        except:
            _log.error(traceback.format_exc())
            await r_utils.Reply(m, "参数错误")

    def UpdateCheck(self) -> str:
        try:
            get = requests.get("https://www.resonance-columba.com/api/get-prices")
            online_products = get.json()["data"]
            content = ""
            content = content + self.Check("桦石发财树", online_products, 90)
            content = content + self.Check("火澄石", online_products, 90)
            content = content + self.Check("负片炮弹", online_products, 90)
            content = content + self.Check("阿妮塔小型桦树发电机", online_products, 90)
            _log.info(f"检索关键低价商品：{content}")
            if content == "":
                return None
            content = f"@全体成员：买入Timing!\n\n{content}"
            return content
        except:
            _log.error(traceback.format_exc())

    def Check(self, product_name, online_products, target) -> str:
        if product_name not in online_products:
            return ""
        product = online_products[product_name]
        now = g_utils.GetCurrentSecondTimeStamp()
        if "buy" in product:
            content = ""
            for city_name in product["buy"]:
                time = product["buy"][city_name]["time"]
                trend = product["buy"][city_name]["trend"]
                variation = product["buy"][city_name]["variation"]
                if now - time >= 3600:
                    continue
                if target < variation:
                    continue
                report_key = f"{city_name}_{product_name}"
                report = f"{city_name} {product_name} {variation} {'↑'if trend=='up' else '↓'}"
                if report_key not in self.already_report:
                    self.already_report[report_key] = ""
                if self.already_report[report_key] == report:
                    continue
                self.already_report[report_key] = report
                content = content + report + "\n"
            return content
        return ""
