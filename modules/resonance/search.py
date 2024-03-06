import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import Message


import modules.resonance.configs.city_id as city_id
import modules.resonance.configs.items_buy as items_buy

_log = logging.get_logger()


async def Search(self, message: Message):
    if "/SearchBasic" in message.content:
        await SearchBasic(self, message)
    return


# 查询商品基础信息
async def SearchBasic(self, message: Message):
    params = message.content.split(" ")
    if len(params) == 3:
        try:
            id = int(params[2])
        except:
            id = params[2]
            for item_id in items_buy.Datas:
                item = items_buy.Datas[item_id]
                if item["name"] == params[2]:
                    id = item_id
                    break
        if isinstance(id, int) and items_buy.Datas[id]:
            item = items_buy.Datas[id]
            city_name = "NULL"
            for key_name in city_id.Datas:
                city = city_id.Datas[key_name]
                if city["id"] == item["city"]:
                    city_name = city["name"]
                    break
            await message.reply(
                content=f"查询道具：{item['name']}\n所属地点：{city_name}\n基础数量：{item['num']}\n基础价格：{item['price']}"
            )
        else:
            _log.info(f"error:不存在道具 {id}")
    else:
        _log.info("error:参数数量不匹配")
