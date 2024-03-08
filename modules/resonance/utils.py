from modules.message_info import MessageInfo
from modules.resonance.configs.items import Datas as ItemData
from modules.resonance.configs.city import Datas as CityData
from modules.resonance.commands.report_buy import BuyInfos
from modules.resonance.commands.report_sell import SellInfos


# 通过ItemID和CityID得到唯一的Item
def GetOnlyItemIDWithCityID(item_ids: list[str], city_id: str):
    for i in item_ids:
        if ItemData[i]["city"] == city_id:
            return i
    return None


# 回复
async def Reply(message_info: MessageInfo, content: str):
    await message_info.message.reply(content=f"@{message_info.author_name}\n\n{content}")


# 查找商品ID
def FindItemIDs(name: str) -> list[str]:
    out = []
    # 说明输入的ID
    if name in ItemData:
        out.append(name)
    # 说明输入的是商品名字母缩写或商品名
    else:
        name = name.lower()
        for item_id in ItemData:
            item_name = ItemData[item_id]["name"]
            item_key = ItemData[item_id]["key"]
            if name in item_name or name in item_key:
                out.append(item_id)
    if len(out) > 0:
        return out
    return None


# 查找商品ID
def FindItemIDsByFullSearch(name: str) -> list[str]:
    out = []
    # 说明输入的ID
    if name in ItemData:
        out.append(name)
    # 说明输入的是商品名字母缩写或商品名
    else:
        name = name.lower()
        for item_id in ItemData:
            if name == ItemData[item_id]["name"] or name == ItemData[item_id]["key"]:
                out.append(item_id)
    if len(out) > 0:
        return out
    return None


# 通过城市ID 查找唯一商品ID
def FindOnlyItemWithCityID(name: str, city_id: str) -> str:
    # 说明输入的ID
    if name in ItemData and ItemData[name]["city"] == city_id:
        return name
    # 说明输入的是商品名字母缩写或商品名
    else:
        name = name.lower()
        for item_id in ItemData:
            item_name = ItemData[item_id]["name"]
            item_key = ItemData[item_id]["key"]
            if ItemData[item_id]["city"] == city_id and (name in item_name or name in item_key):
                return item_id
    return None


# 检查商品列表内是否都是同一种商品，因为模糊匹配可能匹配到多个商品
def CheckItemAllSame(item_ids: list[str]) -> bool:
    item_name = ItemData[item_ids[0]]["name"]
    for id in item_ids:
        if ItemData[id]["name"] != item_name:
            return False
    return True


# 查找城市ID，支持模糊匹配，可能查到多个
def TryFindCityIDs(name: str) -> list[str]:
    out = []
    # 说明输入的ID
    if name in CityData:
        out.append(name)
    # 说明输入的是城市名字母缩写或者城市名
    else:
        name = name.lower()
        for city_id in CityData:
            if name in CityData[city_id]["name"] or name in CityData[city_id]["key"]:
                out.append(city_id)
    if len(out) > 0:
        return out
    return None


def Save():
    with open("save_buy.txt", "w") as f:
        for item_id in BuyInfos.reports:
            for city_id in BuyInfos.reports[item_id]:
                info = BuyInfos.reports[item_id][city_id]
                if info.report_time == 0:
                    continue
                f.write(f"{item_id} {city_id} {info.percentage} {info.report_time}\n")
    with open("save_sell.txt", "w") as f:
        for item_id in SellInfos.reports:
            for city_id in SellInfos.reports[item_id]:
                info = SellInfos.reports[item_id][city_id]
                if info.report_time == 0:
                    continue
                f.write(f"{item_id} {city_id} {info.percentage} {info.report_time}\n")


def Read():
    with open("save_buy.txt", "r") as f:
        line = f.readline()
        while line and line != "":
            params = line.split(" ")
            item_id = int(params[0])
            city_id = int(params[1])
            percentage = float(params[2])
            report_time = float(params[3])
            BuyInfos.Refresh(item_id, city_id, percentage, report_time)
            line = f.readline()
    with open("save_sell.txt", "r") as f:
        line = f.readline()
        while line and line != "":
            params = line.split(" ")
            item_id = int(params[0])
            city_id = int(params[1])
            percentage = float(params[2])
            report_time = float(params[3])
            SellInfos.Refresh(item_id, city_id, percentage, report_time)
            line = f.readline()
