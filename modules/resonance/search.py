import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import Message

from datetime import datetime

import modules.resonance.configs.city_id as city_id
import modules.resonance.configs.items_buy as items_buy
import modules.resonance.configs.items_sell as items_sell
import modules.resonance.report as report

_log = logging.get_logger()


async def Search(self, message: Message):
    if "/SearchBasic" in message.content:
        await SearchBasic(self, message)
    elif "/SearchBuy" in message.content:
        await SearchBuy(self, message)
    return


# 获取道具的ID
def GetItemId(param: str) -> int:
    id = 0
    try:
        id = int(param)
    except:
        id = 0
        for item_id in items_buy.Datas:
            item = items_buy.Datas[item_id]
            if item["name"] == param:
                id = item_id
                break
    return id


# 获取城市信息
def GetCityInfo(id: int):
    for key_name in city_id.Datas:
        city = city_id.Datas[key_name]
        if city["id"] == id:
            return city
    return None


# 获取道具的城市信息
def GetItemCityInfo(item_id: int):
    if item_id in items_buy.Datas:
        return GetCityInfo(items_buy.Datas[item_id]["city"])
    return None


# 查询商品基础信息
async def SearchBasic(self, message: Message):
    params = message.content.split(" ")
    # 查询基础购入价格
    if len(params) == 3:
        id = GetItemId(params[2])
        if id in items_buy.Datas:
            item = items_buy.Datas[id]
            city_name = "NULL"
            city = GetCityInfo(item["city"])
            if city:
                city_name = city["name"]
            await message.reply(
                content=f"查询道具基础购价：{item['name']}\n所属地点：{city_name}\n基础数量：{item['num']}\n基础购入价格：{item['price']}"
            )
        else:
            _log.info(f"error:不存在道具 {id}")
    # 查询在所有城市的售价
    elif len(params) == 4 and (params[3] == "all" or params[3] == "ALL"):
        id = GetItemId(params[2])
        if id in items_buy.Datas and id in items_sell.Datas:
            city_name = "NULL"
            city = GetCityInfo(items_buy.Datas[id]["city"])
            if city:
                city_name = city["name"]
            belong = city_name
            content = f"查询道具基础售价：{items_buy.Datas[id]['name']}\n所属地点：{city_name}\n基础购价：{items_buy.Datas[id]['price']}\n\n"
            for city_id in items_sell.Datas[id]:
                city_name = "NULL"
                city = GetCityInfo(city_id)
                if city:
                    city_name = city["name"]
                if city_name != belong:
                    content = (
                        content + f"{city_name}  {items_sell.Datas[id][city_id]}\n"
                    )
            await message.reply(content=content)
        else:
            _log.info(f"error:不存在道具 {id}")
    else:
        _log.info("error:参数数量不匹配")


async def SearchBuy(self, message: Message):
    params = message.content.split(" ")
    if len(params) != 3:
        return
    item_id = GetItemId(params[2])
    if item_id in report.BuyInfos:
        buyInfo = report.BuyInfos[item_id]
        item_name = items_buy.Datas[buyInfo.item_id]["name"]
        city_info = GetItemCityInfo(item_id)
        percentage = buyInfo.percentage
        now = datetime.timestamp(datetime.now())
        if now - buyInfo.report_time > 600:
            valid = "失效"
        else:
            valid = "有效"
        if buyInfo.state == "1":
            state = "↑"
        else:
            state = "↓"
        await message.reply(
            content=f"购入商品：{item_name}\n所属地：{city_info['name']}\n市值：{percentage}%\n趋势：{state}({valid})"
        )
    else:
        await message.reply(content="暂时没有该商品的出售信息")
    pass
