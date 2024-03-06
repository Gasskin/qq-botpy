import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import Message

from datetime import datetime

import modules.resonance.configs.city_id as city_id
import modules.resonance.configs.city_distance as city_distance
import modules.resonance.configs.items_buy as items_buy
import modules.resonance.configs.items_sell as items_sell
import modules.resonance.report as report

_log = logging.get_logger()


async def Search(self, message: Message):
    if "/SearchBasic" in message.content:
        await SearchBasic(self, message)
    elif "/SearchBuy" in message.content:
        await SearchBuy(self, message)
    elif "/SearchSell" in message.content:
        await SearchSell(self, message)
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


# 获取城市的ID
def GetCityId(param: str) -> int:
    id = 0
    try:
        id = int(param)
    except:
        id = 0
        for city_key in city_id.Datas:
            if city_key == param:
                id = city_id.Datas[city_key]["id"]
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


# 城市1到城市2的距离
def GetCityDistance(city1: int, city2: int) -> float:
    if city1 in city_distance.Datas:
        data = city_distance.Datas[city1]
        if city2 in data:
            return data[city2]
    return 0


# 道具在城市的基础价格
def GetItemBasicPriceInCity(item_id: int, city_id: int) -> float:
    if item_id in items_sell.Datas:
        item = items_sell.Datas[item_id]
        if city_id in item:
            return item[city_id]
    return 0


# 获取商品的购入信息
def GetBuyInfo(item_id):
    if item_id in report.BuyInfos:
        buyInfo = report.BuyInfos[item_id]
        item_name = items_buy.Datas[item_id]["name"]
        city_info = GetItemCityInfo(item_id)

        now = datetime.timestamp(datetime.now())
        if now - buyInfo.report_time <= 600:
            valid = "有效"
        elif now - buyInfo.report_time <= 3600:
            valid = "未知"
        else:
            valid = "失效"
        return {
            "item_name": item_name,
            "city_info": city_info,
            "percentage": buyInfo.percentage,
            "valid": valid,
        }
    return None


# 获取某个商品在某个城市的销售信息
def GetSellInfo(item_id: int, city_id: int):
    if item_id in report.SellInfos:
        sell_infos = report.SellInfos[item_id]
        item_name = items_buy.Datas[item_id]["name"]
        item_price = items_buy.Datas[item_id]["price"]
        now = datetime.timestamp(datetime.now())
        sell_info = sell_infos[city_id]
        if now - sell_info.report_time > 3600:
            return None
        to_city_info = GetCityInfo(city_id)
        distance = GetCityDistance(sell_info.city_info["id"], to_city_info["id"])
        if distance <= 0:
            return None
        to_price = GetItemBasicPriceInCity(item_id, to_city_info["id"])
        if to_price <= 0:
            return None
        valid = "有效" if now - sell_info.report_time <= 600 else "未知"
        buy_info = GetBuyInfo(item_id)
        buy_percentage = 100.0
        if buy_info and buy_info["valid"] != "失效":
            buy_percentage = buy_info["percentage"]

        per_gain = to_price * (sell_info.percentage / 100.0) - item_price * (
            buy_percentage / 100.0
        )

        per_order = per_gain * items_buy.Datas[item_id]["num"]
        return {
            "item_name": item_name,
            "to_city_info": to_city_info,
            "valid": valid,
            "per_gain": round(per_gain, 2),
            "per_order": round(per_order, 2),
            "order_km_gain": round(per_order / distance, 2),
        }
    return None


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
    info = GetBuyInfo(item_id)
    if info:
        await message.reply(
            content=f"购入商品：{info['item_name']}\n所属地：{info['city_info']['name']}\n市值：{info['percentage']}% ({info['valid']})"
        )
    else:
        await message.reply(content="暂时没有该商品的信息")


async def SearchSell(self, message: Message):
    params = message.content.split(" ")
    if len(params) != 3:
        return
    item_id = GetItemId(params[2])
    flag = False
    if item_id in report.SellInfos:
        sellInfos = report.SellInfos[item_id]
        content = f"想要出售的商品：{items_buy.Datas[item_id]['name']}\n"
        for city_id in sellInfos:
            info = GetSellInfo(item_id, city_id)
            if not info:
                continue
            flag = True
            content = (
                content
                + f"城市：{info['to_city_info']['name']} {info['valid']}   {info['per_gain']}/每个  {info['per_order']}/每单  {info['order_km_gain']}/每单每公里\n"
            )
        if flag:
            await message.reply(content=content)
            return
    await message.reply(content="暂时没有该商品的信息")
