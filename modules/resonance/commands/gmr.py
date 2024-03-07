from modules.message_info import MessageInfo
from modules.base_handle import BaseHandle
from modules.resonance import utils as r_utils
from modules.resonance.configs import items
from modules.resonance.configs import citiy


class GMR(BaseHandle):
    async def HandleMessage(self, message_info: MessageInfo):
        function_name = "Function_" + message_info.params[0]
        function = getattr(self, function_name)
        if function:
            content = function(message_info)
        else:
            content = "参数错误"
        await message_info.message.reply(
            content=f"@{message_info.author_name}\n\n{content}"
        )

    # 检索道具表
    def Function_101(self, message_info: MessageInfo) -> str:
        flag, id = r_utils.TryStr2Int(message_info.params[1])
        # 说明输入的ID
        if flag:
            if id in items.Datas:
                return str(items.Datas[id])
        # 说明输入的是商品名字母缩写
        elif r_utils.IsStrAllAlpha(id):
            id = id.lower()
            for item_id in items.Datas:
                if items.Datas[item_id]["key"] == id:
                    return str(items.Datas[item_id])
        # 说明输入的是商品名
        else:
            for item_id in items.Datas:
                if items.Datas[item_id]["name"] == id:
                    return str(items.Datas[item_id])

        return f"不存在商品：{message_info.params[1]}"

    # 检索城市表
    def Function_102(self, message_info: MessageInfo) -> str:
        flag, id = r_utils.TryStr2Int(message_info.params[1])
        # 说明输入的ID
        if flag:
            if id in citiy.Datas:
                return str(citiy.Datas[id])
        # 说明输入的是城市名字母缩写
        elif r_utils.IsStrAllAlpha(id):
            id = id.lower()
            for city_id in citiy.Datas:
                if citiy.Datas[city_id]["key"] == id:
                    return str(citiy.Datas[city_id])
        # 说明输入的是城市名
        else:
            for city_id in citiy.Datas:
                if citiy.Datas[city_id]["name"] == id:
                    return str(citiy.Datas[city_id])

        return f"不存在城市：{message_info.params[1]}"
