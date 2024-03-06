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
    percentage: str = ""
    # 趋势
    state: str = ""

    def __init__(self, item_id, city_info, percentage, state) -> None:
        self.item_id = item_id
        self.city_info = city_info
        self.Refresh(percentage, state)

    def Refresh(self, percentage, state):
        self.report_time = datetime.timestamp(datetime.now())
        self.percentage = percentage
        self.state = state


BuyInfos: dict[int, ReportInfo] = {}

SellInfos = {}


async def Report(self, message: Message):
    if "/ReportBuy" in message.content:
        await ReportBuy(self, message)
    elif "/ReportSell" in message.content:
        await ReportSell(self, message)
    return


async def ReportBuy(self, message: Message):
    params = message.content.split(" ")
    if len(params) != 5:
        return
    item_id = search.GetItemId(params[2])
    city_info = search.GetItemCityInfo(item_id)
    percentage = params[3]
    state = params[4]
    if not item_id or not city_info or not percentage:
        return
    if item_id not in BuyInfos:
        BuyInfos[item_id] = ReportInfo(item_id, city_info, percentage, state)
    else:
        BuyInfos[item_id].Refresh(percentage, state)
    return


async def ReportSell(self, message: Message):
    return
