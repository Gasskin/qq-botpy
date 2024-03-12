import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import Message

from modules.message_info import MessageInfo
from modules import utils as utils
import asyncio
import modules.resonance
from modules import global_config as G_Config

_log = logging.get_logger()

Resonance = modules.resonance.Resonance()


class MyClient(botpy.Client):
    REPLY = {
        "/GMR": "连接机器人成功",
        "/SearchBuy": "没有查到相关买入信息",
        "/SearchSell": "没有查到相关销售信息",
        "/RecommendSell": "暂时没有商品推荐",
    }

    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")
        while True:
            res = Resonance.UpdateCheck()
            if res:
                await self.api.post_message(channel_id=G_Config.CHANNEL_1, content=res)
            await asyncio.sleep(60)

    async def on_at_message_create(self, message: Message):
        _log.info(f"\n发送人：{message.author.username} {message.author.id} {message.timestamp}\n发送内容：{message.content}")
        if not message.content.endswith(G_Config.INTERVAL):
            for key in self.REPLY:
                if key in message.content:
                    return await message.reply(content=f"{self.REPLY[key]}")
            return await message.reply(content="你好！")
        message.content = message.content.replace(G_Config.INTERVAL, "")
        message_info = MessageInfo()
        message_info.InitWithMessage(message)

        if Resonance.FilterMeesage(message_info):
            return await Resonance.HandleMessage(message_info)
        return await message.reply(content="没有能够执行该命令的模块")


if __name__ == "__main__":
    bot_index = "1"
    intents = botpy.Intents(direct_message=True, public_guild_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=getattr(G_Config, "APPID_" + bot_index), secret=getattr(G_Config, "SECRET_" + bot_index))
