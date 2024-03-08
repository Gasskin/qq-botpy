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


# 查找商品ID，可能有多个
def TryFindItemIDs(name: str) -> list[str]:
    out = []
    # 说明输入的ID
    if name in ItemData:
        out.append(name)
        return name
    # 说明输入的是商品名字母缩写或商品名
    else:
        name = name.lower()
        for item_id in ItemData:
            if ItemData[item_id]["name"] == name or ItemData[item_id]["key"] == name:
                out.append(item_id)
        if len(out) > 0:
            return out
    return None


# 查找城市ID，不会重复
def TryFindCityID(name: str):
    # 说明输入的ID
    if name in CityData:
        return name
    # 说明输入的是城市名字母缩写或者城市名
    else:
        name = name.lower()
        for city_id in CityData:
            if CityData[city_id]["name"] == name or CityData[city_id]["key"] == name:
                return city_id
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
