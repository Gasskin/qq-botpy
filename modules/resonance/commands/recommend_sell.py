from modules import utils as g_utils
from modules.message_info import MessageInfo
from modules.base_handle import BaseHandle
from modules.resonance import utils as r_utils
from modules.resonance.configs.product import Datas as ProductDatas
from modules import global_config as G_Config
from botpy import logging

import requests
import traceback

_log = logging.get_logger()


# 单个商品销售信息
class SellProductInfo(object):
    product_name: str
    from_city: str
    to_city: str
    income: float
    description: str

    def __init__(self) -> None:
        return


# 城市间的来回信息
class RouteResult(object):
    route: str = ""
    to_income: float = 0
    to_description: str = ""
    back_income: float = 0
    back_description: str = ""

    def __init__(self) -> None:
        return


class RecommendSell(BaseHandle):
    # 城市名
    city: list[str]
    # 商品信息：商品名/商品信息
    products: dict[str, dict]
    # 城市商品信息：城市名/商品名
    city_special_products = dict[str, list[str]]
    city_normal_products = dict[str, list[str]]
    # 当前价格信息
    #     "发动机": {
    #         "buy": {
    #             "修格里城": {
    #                 "trend": "up",
    #                 "variation": 110,
    #                 "time": 1710124604
    #             }
    #         },
    #         "sell": {
    #             "修格里城": {
    #                 "trend": "up",
    #                 "time": 1709575136
    #            },
    #             "铁盟哨站": {
    #                 "trend": "up",
    #                 "variation": 92,
    #                 "time": 1710040779
    #             ......
    #         }
    # },
    online_products = None

    def __init__(self) -> None:
        super().__init__()
        self.products = {}
        self.city_special_products = {}
        self.city_normal_products = {}
        for data in ProductDatas:
            procudt_name = data["name"]
            if procudt_name in self.products:
                _log.error(f"重复的商品名：{procudt_name}")
                continue
            self.products[data["name"]] = data

            if data["type"] == "Special":
                for city_name in data["buyPrices"]:
                    if city_name not in self.city_special_products:
                        self.city_special_products[city_name] = []
                    self.city_special_products[city_name].append(procudt_name)
            elif data["type"] == "Normal":
                for city_name in data["buyPrices"]:
                    if city_name not in self.city_normal_products:
                        self.city_normal_products[city_name] = []
                    self.city_normal_products[city_name].append(procudt_name)

        self.city = []
        for key in ProductDatas[0]["sellPrices"]:
            self.city.append(key)

    # 无参数，排序所有城市的来回路线收益
    async def HandleMessage(self, m: MessageInfo):
        try:
            proxy = G_Config.PROXY
            get = requests.get(G_Config.GET_PRICE_V2, proxies=proxy)
            self.online_products = get.json()["data"]
            all = self.GetRouteResult()
            max = 3 if len(all) > 3 else len(all)
            content = ""
            max_income = all[0].to_income + all[0].back_income
            for i in range(0, max):
                result = all[i]
                route_income = result.to_income + result.back_income
                content += f"{result.route} ({round(route_income/max_income*100)}%)\n{result.to_description}\n{result.back_description}\n\n"
            await r_utils.Reply(m, content=content)
        except:
            _log.error(traceback.format_exc())
            await r_utils.Reply(m, "参数错误")

    # 计算从from_city到其他所有城市的路线收益
    def GetRouteResult(self) -> list[RouteResult]:
        out: list[RouteResult] = []

        for i in range(0, len(self.city) - 1):
            for j in range(i + 1, len(self.city)):
                from_city = self.city[i]
                to_city = self.city[j]
                if from_city == to_city:
                    continue

                to_info = self.GetCityRouteInfo(from_city, to_city)
                back_info = self.GetCityRouteInfo(to_city, from_city)

                route_result = RouteResult()
                route_result.route = f"{from_city} <==> {to_city}"

                # 先计算各自的利润
                for sell_info in to_info:
                    route_result.to_income += sell_info.income
                for sell_info in back_info:
                    route_result.back_income += sell_info.income
                # 计算一些描述信息
                route_result.to_description = f"to：{round(route_result.to_income,1)}/单"
                for sell_info in to_info:
                    percentage = round(sell_info.income / route_result.to_income * 100, 1)
                    route_result.to_description += f"\n{sell_info.product_name} {sell_info.description} ({percentage}%)"

                route_result.back_description = f"back：{round(route_result.back_income,1)}/单"
                for sell_info in back_info:
                    percentage = round(sell_info.income / route_result.back_income * 100, 1)
                    route_result.back_description += f"\n{sell_info.product_name} {sell_info.description} ({percentage}%)"
                out.append(route_result)
        out.sort(key=lambda x: x.to_income + x.back_income, reverse=True)
        return out

    # 计算从from_city到to_city的商品利润信息
    def GetCityRouteInfo(self, from_city, to_city) -> list[SellProductInfo]:
        special_products = self.city_special_products[from_city]
        normal_products = self.city_normal_products[from_city]

        route_info: list[SellProductInfo] = []
        for product_name in special_products:
            if product_name not in self.products:
                continue
            product_info = self.GetSellProductInfo(product_name, from_city, to_city)
            if product_info != None:
                route_info.append(product_info)
        for product_name in normal_products:
            if product_name not in self.products:
                continue
            product_info = self.GetSellProductInfo(product_name, from_city, to_city)
            if product_info != None:
                route_info.append(product_info)
        route_info.sort(key=lambda x: x.income, reverse=True)
        return route_info

    def GetSellProductInfo(self, product_name: str, from_city: str, to_city: str) -> SellProductInfo:
        try:
            now = g_utils.GetCurrentSecondTimeStamp()
            # 在线信息
            buy_info = self.online_products[product_name]["buy"][from_city]
            sell_info = self.online_products[product_name]["sell"][to_city]
            if now - buy_info["time"] >= 3600 or now - sell_info["time"] >= 3600:
                return None
            if "trend" not in buy_info or "trend" not in sell_info:
                return None
            if "variation" not in buy_info or "variation" not in sell_info:
                return None
            if buy_info["variation"] <= 0 or sell_info["variation"] <= 0:
                return None

            # 本地信息
            product_info = self.products[product_name]
            buy_price = product_info["buyPrices"][from_city]
            buy_lot = product_info["buyLot"][from_city]
            sell_price = product_info["sellPrices"][to_city]

            if buy_price * buy_info["variation"] >= sell_price * sell_info["variation"]:
                return None

            sell_product_info = SellProductInfo()
            sell_product_info.product_name = product_name
            sell_product_info.from_city = from_city
            sell_product_info.to_city = to_city

            buy_variation = buy_info["variation"] / 100.0
            sell_variation = sell_info["variation"] / 100.0
            buy = buy_price * buy_variation * buy_lot

            sell_product_info.income = sell_price * sell_variation * buy_lot - buy

            from_trend = "↑" if buy_info["trend"] == "up" else "↓"
            to_trend = "↑" if buy_info["trend"] == "up" else "↓"
            sell_product_info.description = f"{buy_info['variation']}{from_trend} --> {sell_info['variation']}{to_trend}"

            return sell_product_info
        except:
            return None
