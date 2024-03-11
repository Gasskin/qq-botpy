from modules.message_info import MessageInfo
from modules.resonance.configs.city import Datas as CityData


# 回复
async def Reply(message_info: MessageInfo, content: str):
    await message_info.message.reply(content=f"@{message_info.author_name}\n\n{content}")


# 查找城市ID，支持模糊匹配，可能查到多个
def FindCityNames(name: str) -> list[str]:
    out = []
    # 说明输入的ID
    if name in CityData:
        out.append(name)
    # 说明输入的是城市名字母缩写或者城市名
    else:
        name = name.lower()
        for city_name in CityData:
            if name in city_name or name in CityData[city_name]["key"]:
                out.append(city_name)
    if len(out) > 0:
        return out
    return None
