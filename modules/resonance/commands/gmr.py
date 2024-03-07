from modules.message_info import MessageInfo
from modules.base_handle import BaseHandle
from modules.resonance import utils as r_utils
from modules.resonance.configs import items
from modules.resonance.configs import city
from modules.resonance.commands.report_sell import SellInfos
from modules.resonance.commands.report_buy import BuyInfos

class GMR(BaseHandle):
    async def HandleMessage(self, message_info: MessageInfo):
        function_name = "Function_" + message_info.params[0]
        function = getattr(self, function_name)
        if function:
            content = function(message_info)
        else:
            content = "参数错误"
        await r_utils.Reply(message_info, content)

    # 检索道具表
    def Function_101(self, message_info: MessageInfo) -> str:
        try:
            item_ids = r_utils.TryFindItemIDs(message_info.params[1])
            if item_ids:
                str = ""
                for key in item_ids:
                    item_id = item_ids[key]
                    str = str + "\n\n" + str(items.Datas[item_id])
                return str
            return f"不存在商品：{message_info.params[1]}"
        except:
            return "GM 101 参数错误"

    # 检索城市表
    def Function_102(self, message_info: MessageInfo) -> str:
        try:
            city_id = r_utils.TryFindCityID(message_info.params[1])
            if city_id:
                return str(city.Datas[city_id])
            return f"不存在城市：{message_info.params[1]}"
        except:
            return "GM 102 参数错误"

    # 当前的销售情况
    def Function_103(self, message_info: MessageInfo) -> str:
        try:
            content = "BuyInfo：\n"
            for item_id in BuyInfos.reports:
                for city_id in BuyInfos.reports[item_id]:
                    info = BuyInfos.reports[item_id][city_id]
                    if info.report_time!=0:
                        content = content + f"{item_id} {city_id} {info.percentage} {info.GetValid()}\n"
            content = content + "SellInfo：\n"
            for item_id in SellInfos.reports:
                for city_id in SellInfos.reports[item_id]:
                    info = SellInfos.reports[item_id][city_id]
                    if info.report_time!=0:
                        content = content+f"{item_id} {city_id} {info.percentage} {info.GetValid()}\n"
            return content
        except:
            return "GM 103 参数错误"

    def Function_SAVE(self, message_info: MessageInfo) -> str:
        try:
            r_utils.Save()
            return "保存成功"
        except:
            return "GM SAVE 参数错误"

    def Function_READ(self, message_info: MessageInfo) -> str:
        try:
            r_utils.Read()
            return "读取成功"
        except:
            return "GM READ 参数错误"
