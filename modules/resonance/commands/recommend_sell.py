from modules import utils as g_utils
from modules.message_info import MessageInfo
from modules.base_handle import BaseHandle
from modules.resonance import utils as r_utils
from modules.resonance.configs.product import Datas as ProductDatas
from modules.resonance.configs.city import Datas as CityDatas
from botpy import logging
import requests
import traceback

_log = logging.get_logger()


# 销售信息
class RouteInfo(object):
    product_name: str
    from_city: str
    to_city: str
    buy_price: float = None
    buy_lot: float = None
    sell_price: float = None
    buy_info = None
    sell_info = None

    def __init__(self) -> None:
        return

    def GetBuyTrendState(self) -> str:
        if self.buy_info["trend"] == "up":
            return "↑"
        return "↓"

    def GetSellTrendState(self) -> str:
        if self.sell_info["trend"] == "up":
            return "↑"
        return "↓"


class RouteResult(object):
    from_city: str
    to_city: str
    income: float
    sell_products: str

    def __init__(self) -> None:
        return

    def ToString() -> str:
        pass


class RecommendSell(BaseHandle):
    # 城市名
    city: list[str]
    # 商品信息：商品名/商品信息
    products: dict[str, dict]
    # 城市特产信息：城市名/商品名
    city_special_products = dict[str, list[str]]
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

        self.city = []
        for key in ProductDatas[0]["sellPrices"]:
            self.city.append(key)

    # 1.无参数，排序所有城市
    # 2.城市，推荐特定城市的销售路线
    async def HandleMessage(self, m: MessageInfo):
        try:
            get = requests.get("https://www.resonance-columba.com/api/get-prices")
            self.online_products = get.json()["data"]
            if m.params[0] == "":
                all: list[RouteResult] = []
                for city in self.city:
                    all = all + self.GetRouteResult(city)
                all.sort(key=lambda x: x.income, reverse=True)
                max = 5 if len(all) > 5 else len(all)
                content = "综合推荐：\n"
                for i in range(0, max):
                    result = all[i]
                    content = content + f"from {result.from_city} to {result.to_city} with {result.sell_products}\n{result.income}/单\n"
            else:
                from_citys = r_utils.FindCityNames(m.params[0])
                if not from_citys or len(from_citys) > 1:
                    return await r_utils.Reply(m, "城市名称存在多个匹配项")
                from_city = from_citys[0]
                content = f"from：{from_city}\n"
                route_results = self.GetRouteResult(from_city)
                route_results.sort(key=lambda x: x.income, reverse=True)
                for result in route_results:
                    content = content + f"to {result.to_city} with {result.sell_products}\n{result.income}/单\n"

            await r_utils.Reply(m, content=content)
        except:
            _log.error(traceback.format_exc())
            await r_utils.Reply(m, "参数错误")

    def GetRouteResult(self, from_city) -> list[RouteResult]:
        out: list[RouteResult] = []
        route_infos = self.GetCityRouteInfo(from_city)
        for to_city in route_infos:
            route_list = route_infos[to_city]
            if len(route_list) <= 0:
                continue
            result = RouteResult()
            result.from_city = from_city
            result.to_city = to_city
            result.income = self.GetTotalRouteInCome(route_list)
            result.sell_products = ""
            for route in route_list:
                result.sell_products = result.sell_products + f"{route.product_name}{route.sell_info['variation']}{route.GetSellTrendState()} "
            out.append(result)
        return out

    def GetCityRouteInfo(self, from_city) -> dict[str, list[RouteInfo]]:
        special_products = self.city_special_products[from_city]

        all_routes: dict[str, list[RouteInfo]] = {}
        for to_city in self.city:
            if to_city == from_city:
                continue
            all_routes[to_city] = []
            for product_name in special_products:
                if product_name not in self.products:
                    continue
                route = self.GetProductRouteInfo(product_name, from_city, to_city)
                if route != None:
                    all_routes[to_city].append(route)
        return all_routes

    def GetProductRouteInfo(self, product_name: str, from_city: str, to_city: str):
        try:
            now = g_utils.GetCurrentSecondTimeStamp()
            # 在线信息
            buy_info = self.online_products[product_name]["buy"][from_city]
            sell_info = self.online_products[product_name]["sell"][to_city]
            if now - buy_info["time"] >= 3600 or now - sell_info["time"] >= 3600:
                return None

            # 本地信息
            product_info = self.products[product_name]
            buy_price = product_info["buyPrices"][from_city]
            buy_lot = product_info["buyLot"][from_city]
            sell_price = product_info["sellPrices"][to_city]

            route_info = RouteInfo()
            route_info.product_name = product_name
            route_info.from_city = from_city
            route_info.to_city = to_city

            route_info.buy_price = buy_price
            route_info.buy_lot = buy_lot
            route_info.sell_price = sell_price
            route_info.buy_info = buy_info
            route_info.sell_info = sell_info
            return route_info
        except:
            return None

    def GetTotalRouteInCome(self, routes: list[RouteInfo]):
        buy = 0
        income = 0
        for route in routes:
            buy_variation = route.buy_info["variation"] / 100.0
            sell_variation = route.sell_info["variation"] / 100.0
            buy = buy + route.buy_price * buy_variation * route.buy_lot
            income = income + route.sell_price * sell_variation * route.buy_lot
        return round(income - buy, 1)
