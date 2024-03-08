from modules.message_info import MessageInfo
from modules.base_handle import BaseHandle
from modules.resonance import utils as r_utils
from modules.resonance.configs import items
from modules.resonance.configs import city
from modules.resonance.commands.report_sell import SellInfos
from modules.resonance.commands.report_buy import BuyInfos
from modules.resonance.report_info import ReportInfos


class GMR(BaseHandle):
    WHITE_ID: dict[str, bool] = {"9631977870258360057": True, "0": False}

    async def HandleMessage(self, m: MessageInfo):
        if m.author_id not in self.WHITE_ID:
            return
        if not self.WHITE_ID[m.author_id]:
            return
        function_name = "Function_" + m.params[0]
        function = getattr(self, function_name)
        if function:
            content = function(m)
        else:
            content = "参数错误"
        await r_utils.Reply(m, content)

    # 检索道具表
    def Function_101(self, m: MessageInfo) -> str:
        try:
            if m.params[1].endswith("*"):
                name = m.params[1].replace("*", "")
                item_ids = r_utils.FindItemIDsByFullSearch(name)
            else:
                item_ids = r_utils.FindItemIDs(m.params[1])
            if not item_ids:
                return f"不存在商品：{m.params[1]}"
            if not r_utils.CheckItemAllSame(item_ids):
                return f"{m.params[1]} 存在多个匹配项"
            str = ""
            for item_id in item_ids:
                str = str + "\n\n" + str(items.Datas[item_id])
            return str
        except:
            return "GM 101 参数错误"

    # 检索城市表
    def Function_102(self, m: MessageInfo) -> str:
        try:
            city_ids = r_utils.TryFindCityIDs(m.params[1])
            if not city_ids:
                return f"不存在城市：{m.params[1]}"
            if len(city_ids) > 1:
                return f"{m.params[1]} 存在多个匹配项"
            return str(city.Datas[city_ids[0]])
        except:
            return "GM 102 参数错误"

    # 当前的销售情况
    def Function_103(self, m: MessageInfo) -> str:
        try:
            content = "BuyInfo：\n"
            for item_id in BuyInfos.reports:
                for city_id in BuyInfos.reports[item_id]:
                    info = BuyInfos.reports[item_id][city_id]
                    if info.report_time != 0:
                        content = content + f"{item_id} {city_id} {info.percentage} {info.GetValid()}\n"
            content = content + "SellInfo：\n"
            for item_id in SellInfos.reports:
                for city_id in SellInfos.reports[item_id]:
                    info = SellInfos.reports[item_id][city_id]
                    if info.report_time != 0:
                        content = content + f"{item_id} {city_id} {info.percentage} {info.GetValid()}\n"
            return content
        except:
            return "GM 103 参数错误"

    # 撤回上报 买入/卖出 商品 城市
    def Function_104(self, m: MessageInfo) -> str:
        try:
            info: ReportInfos = None
            if m.params[1] == "1":
                info = BuyInfos
            elif m.params[1] == "0":
                info = SellInfos
            else:
                return "GM 104 参数错误"
            item_id = m.params[2]
            city_id = m.params[3]
            if item_id in info.reports and city_id in info.reports[item_id]:
                info.reports[item_id][city_id].Back()
                return "撤回成功"
            return "不存在商品信息"
        except:
            return "GM 104 参数错误"

    def Function_SAVE(self, m: MessageInfo) -> str:
        try:
            r_utils.Save()
            return "保存成功"
        except:
            return "GM SAVE 参数错误"

    def Function_READ(self, m: MessageInfo) -> str:
        try:
            r_utils.Read()
            return "读取成功"
        except:
            return "GM READ 参数错误"
