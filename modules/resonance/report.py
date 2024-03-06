from datetime import datetime

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import Message


import modules.resonance.configs.city_id as city_id
import modules.resonance.configs.items_buy as items_buy
import modules.resonance.configs.items_sell as items_sell
import modules.resonance.search as search


class ReportInfo(object):
    # 上报时间
    report_time = 0
    # 上报的商品ID
    item_id: int = 0
    # 上报的城市
    city_info = None
    # 上报的市场百分比
    percentage: float = 0.0

    def __init__(self, item_id, city_info, percentage) -> None:
        self.item_id = item_id
        self.city_info = city_info
        self.Refresh(percentage)

    def Refresh(self, percentage):
        self.report_time = datetime.timestamp(datetime.now())
        self.percentage = percentage


BuyInfos: "dict[int, ReportInfo]" = {}

SellInfos: "dict[int, dict[int, ReportInfo]]" = {}


async def Report(self, message: Message):
    if "/ReportBuy" in message.content:
        await ReportBuy(self, message)
    elif "/ReportSell" in message.content:
        await ReportSell(self, message)
    return


async def ReportBuy(self, message: Message):
    params = message.content.split(" ")
    count = len(params)
    if count < 3:
        return
    for i in range(2, count):
        infos = params[i].split(".")
        item_id = search.GetItemId(infos[0])
        city_info = search.GetItemCityInfo(item_id)
        percentage = float(infos[1])
        if not item_id or not city_info or not percentage:
            return
        if item_id not in BuyInfos:
            BuyInfos[item_id] = ReportInfo(item_id, city_info, percentage)
        else:
            BuyInfos[item_id].Refresh(percentage)


async def ReportSell(self, message: Message):
    params = message.content.split(" ")
    count = len(params)
    if count < 4:
        return
    city_id = search.GetCityId(params[2])
    for i in range(3, count):
        infos = params[i].split(".")
        item_id = search.GetItemId(infos[0])
        city_info = search.GetItemCityInfo(item_id)
        percentage = float(infos[1])
        if not city_id or not item_id or not city_info or not percentage:
            return
        if item_id not in SellInfos:
            SellInfos[item_id] = {}
        if city_id not in SellInfos[item_id]:
            SellInfos[item_id][city_id] = ReportInfo(item_id, city_info, percentage)
        else:
            SellInfos[item_id][city_id].Refresh(percentage)
