from modules.message_info import MessageInfo
from modules.base_handle import BaseHandle
from modules.resonance import utils as r_utils
from modules.resonance.configs import items


class GMR(BaseHandle):
    async def HandleMessage(self, message_info: MessageInfo):
        function_name = "Function_" + message_info.params[0]
        function = getattr(self, function_name)
        if function:
            content = function(message_info)
        else:
            content = "参数错误"
        await message_info.message.reply(content=content)

    # 检索道具表
    def Function_101(self, message_info: MessageInfo) -> str:
        flag, id = r_utils.TryStr2Int(message_info.params[1])
        # 说明输入的ID
        if flag:
            if id in items.Datas:
                return str(items.Datas[id])
            else:
                return f"不存在商品：{id}"
        # 说明输入的是商品名字母缩写
        elif r_utils.IsStrAllAlpha(id):
            for item_id in items.Datas:
                if items.Datas[item_id]["key"] == id:
                    return str(items.Datas[item_id])
        # 说明输入的是商品名
        else:
            for item_id in items.Datas:
                if items.Datas[item_id]["name"] == id:
                    return str(items.Datas[item_id])

        return f"不存在商品：{message_info.params[1]}"
