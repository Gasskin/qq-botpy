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


# 销售信息
class SellProductInfo(object):
    product_name: str
    from_city: str
    to_city: str
    income: float
    description: str

    def __init__(self) -> None:
        return


class RouteResult(object):
    from_city: str
    to_city: str
    description: str
    income: float

    def __init__(self) -> None:
        return

    def ToString() -> str:
        pass


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

    # 1.无参数，排序所有城市
    # 2.城市，推荐特定城市的销售路线
    async def HandleMessage(self, m: MessageInfo):
        try:
            get = requests.get(G_Config.GET_PRICE_V2)
            self.online_products = get.json()["data"]
            if m.params[0] == "":
                all: list[RouteResult] = []
                for city in self.city:
                    all = all + self.GetRouteResult(city)
                all.sort(key=lambda x: x.income, reverse=True)
                max = 3 if len(all) > 3 else len(all)
                max_income = all[0].income
                content = "最佳推荐：\n"
                for i in range(0, max):
                    result = all[i]
                    content = content + f"from {result.from_city} to {result.to_city} ({round(result.income/max_income*100,1)}%)\n{result.description}\n"
            else:
                from_citys = r_utils.FindCityNames(m.params[0])
                if not from_citys or len(from_citys) > 1:
                    return await r_utils.Reply(m, "城市名称存在多个匹配项")
                from_city = from_citys[0]
                route_results = self.GetRouteResult(from_city)
                route_results.sort(key=lambda x: x.income, reverse=True)
                max_income = route_results[0].income
                content = f"from：{from_city}\n"
                for result in route_results:
                    content = content + f"to {result.to_city} ({round(result.income/max_income*100,1)}%)\n{result.description}\n"

            await r_utils.Reply(m, content=content)
        except:
            _log.error(traceback.format_exc())
            await r_utils.Reply(m, "参数错误")

    # 计算从from_city到其他所有城市的路线收益
    def GetRouteResult(self, from_city) -> list[RouteResult]:
        out: list[RouteResult] = []
        route_infos = self.GetCityRouteInfo(from_city)
        for to_city in route_infos:
            route = route_infos[to_city]
            if len(route) <= 0:
                continue
            result = RouteResult()
            result.from_city = from_city
            result.to_city = to_city
            result.income = 0
            for sell_product_info in route:
                result.income = result.income + sell_product_info.income

            result.description = ""
            for sell_product_info in route:
                income = sell_product_info.income
                result.description = result.description + f"{sell_product_info.product_name} {sell_product_info.description} ({round(income/result.income*100,1)}%)\n"
            out.append(result)
        return out

    # 计算从from_city到其他所有城市的特殊商品销售信息
    # 修格里城->淘金乐园[发动机，弹丸加速装置]
    def GetCityRouteInfo(self, from_city) -> dict[str, list[SellProductInfo]]:
        special_products = self.city_special_products[from_city]
        normal_products = self.city_normal_products[from_city]
        all_routes: dict[str, list[SellProductInfo]] = {}
        for to_city in self.city:
            if to_city == from_city:
                continue
            all_routes[to_city] = []
            for product_name in special_products:
                if product_name not in self.products:
                    continue
                product_info = self.GetSellProductInfo(product_name, from_city, to_city)
                if product_info != None:
                    all_routes[to_city].append(product_info)
            for product_name in normal_products:
                if product_name not in self.products:
                    continue
                product_info = self.GetSellProductInfo(product_name, from_city, to_city)
                if product_info != None:
                    all_routes[to_city].append(product_info)
            all_routes[to_city].sort(key=lambda x: x.income, reverse=True)
        return all_routes

    def GetSellProductInfo(self, product_name: str, from_city: str, to_city: str):
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
