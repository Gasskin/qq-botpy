from modules import utils as g_utils
from modules.message_info import MessageInfo
from modules.base_handle import BaseHandle
from modules.resonance import utils as r_utils
from modules.resonance.configs.city import Datas as CityData
from modules.resonance.configs.items import Datas as ItemData
from modules.resonance.commands.report_buy import BuyInfos
from modules.resonance.commands.report_sell import SellInfos
from botpy import logging

import traceback

_log = logging.get_logger()

#收益
class InCome(object):
    get:float           #每单收入
    get_per_km:float    #每单每公里收入
    from_name:str       #购入地名称
    to_name:str         #销售地名称
    from_valid:float    #购入地信息有效值
    to_valid:float      #卖出地信息有效值
    def __init__(self) -> None:
        pass

class RecommendSell(BaseHandle):
    #城市 商品A 商品B
    async def HandleMessage(self, m: MessageInfo):
        try:
            city_id = r_utils.TryFindCityID(m.params[0])
            if not city_id:
                return await r_utils.Reply(m, f"不存在城市：{m.params[0]}")
            target = []
            for i in range(1,len(m.params)):
                item_ids = r_utils.TryFindItemIDs(m.params[i])
                if not item_ids:
                    return await r_utils.Reply(m, f"不存在商品：{m.params[i]}")
                item_id = r_utils.GetOnlyItemIDWithCityID(item_ids,city_id)
                if not item_id:
                    return await r_utils.Reply(m, f"商品：{m.params[i]} 不属于城市{m.params[0]}")
                target.append(item_id)
        
            total_income : "list[list[InCome]]" = []
            for i in CityData:
                if i == city_id:
                    continue
                income:"list[InCome]" = []
                for j in target:
                    income.append(self.GetInCome(j,city_id,i))
                total_income.append(income)
            name = ""
            for i in target:
                name = name +ItemData[i]['name']+" +" 
            total_income.sort(key=self.SrotInCome,reverse=True)
            return await r_utils.Reply(m, f"{name} {self.GetContent(total_income)}")
        except Exception as e:
            _log.error(traceback.format_exc())
            _log.error(e)
            await r_utils.Reply(m, "参数错误")

    def SrotInCome(self,income:"list[InCome]")->float:
        total = 0
        for i in income:
            total = total + i.get
        return total

    def GetContent(self,total_income:"list[list[InCome]]"):
        content = f"from：{total_income[0][0].from_name}\n"
        for income in total_income:
            get = 0
            get_per_km = 0
            valid = 0
            totoal_valid = 0
            for j in income:
                get = get + j.get
                get_per_km = get_per_km + j.get_per_km
                totoal_valid = totoal_valid + 2
                valid = valid + j.from_valid + j.to_valid
            content = content + f"to：{income[0].to_name} {round(get,1)}/单 信息有效值：{round(valid/totoal_valid,1)}\n"
        return content

    def GetInCome(self,item_id:int,from_city:int,to_city:int)->InCome:
        #买入地的购入信息
        from_buy_info = BuyInfos.GetAndAddDefaultIfNone(item_id,from_city)
        #卖出地的销售信息
        to_sell_info = SellInfos.GetAndAddDefaultIfNone(item_id,to_city)
        #基础购入价格
        from_base_price = ItemData[item_id]["buy_price"]
        #基础售出价格
        to_base_price = ItemData[item_id]["sell_price"][to_city]
        #两地距离
        distance = CityData[from_city]['distance'][to_city]
        #每单数量
        num = ItemData[item_id]['num']

        from_price = from_base_price * (from_buy_info.percentage/100.0)
        to_price = to_base_price*(to_sell_info.percentage/100.0)

        get = round((to_price - from_price)*num,1)
        get_per_km = round(get/distance,1)
        from_name = CityData[from_city]['name']
        to_name = CityData[to_city]['name']

        income = InCome()
        income.get = get
        income.get_per_km = get_per_km
        income.from_name = from_name
        income.to_name = to_name
        income.from_valid = from_buy_info.GetValidValue()
        income.to_valid = to_sell_info.GetValidValue()
        
        return income