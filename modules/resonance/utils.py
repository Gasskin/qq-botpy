from modules.message_info import MessageInfo
from modules.resonance.configs import items
from modules.resonance.configs import city
from modules.resonance.commands.report_buy import BuyInfos
from modules.resonance.commands.report_sell import SellInfos


# 检测字符串是不是全是英文字母
def IsStrAllAlpha(str: str) -> bool:
    return str.encode().isalpha()


# 尝试把str转为int，如果失败了返回字符串自身
def TryStr2Int(str: str):
    try:
        res = int(str)
        return True, res
    except:
        return False, str


# 回复
async def Reply(message_info: MessageInfo, content: str):
    await message_info.message.reply(
        content=f"@{message_info.author_name}\n\n{content}"
    )


# 查找商品ID，可能有多个
def TryFindItemIDs(item_str: str):
    flag, id = TryStr2Int(item_str)
    # 说明输入的ID
    if flag:
        if id in items.Datas:
            return id
    # 说明输入的是商品名字母缩写
    elif IsStrAllAlpha(id):
        out = []
        id = id.lower()
        for item_id in items.Datas:
            if items.Datas[item_id]["key"] == id:
                out.append(item_id)
        if len(out) > 0:
            return out
    # 说明输入的是商品名
    else:
        out = []
        for item_id in items.Datas:
            if items.Datas[item_id]["name"] == id:
                out.append(item_id)
        if len(out) > 0:
            return out
    return None


# 查找城市ID，不会重复
def TryFindCityID(city_str: str):
    flag, id = TryStr2Int(city_str)
    # 说明输入的ID
    if flag:
        if id in city.Datas:
            return id
    # 说明输入的是城市名字母缩写
    elif IsStrAllAlpha(id):
        id = id.lower()
        for city_id in city.Datas:
            if city.Datas[city_id]["key"] == id:
                return city_id
    # 说明输入的是城市名
    else:
        for city_id in city.Datas:
            if city.Datas[city_id]["name"] == id:
                return city_id
    return None


def Save():
    with open("save_buy.txt", "w") as f:
        for item_id in BuyInfos.reports:
            for city_id in BuyInfos.reports[item_id]:
                info = BuyInfos.reports[item_id][city_id]
                f.write(f"{item_id} {city_id} {info.percentage} {info.report_time}\n")
    with open("save_sell.txt", "w") as f:
        for item_id in SellInfos.reports:
            for city_id in SellInfos.reports[item_id]:
                info = SellInfos.reports[item_id][city_id]
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
