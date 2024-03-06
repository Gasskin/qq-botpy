import asyncio
import os

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import Message

import modules.resonance.search
import modules.resonance.report

_log = logging.get_logger()

# 配置
CONFIG = read(os.path.join(os.path.dirname(__file__), "config.yaml"))


class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_at_message_create(self, message: Message):
        _log.info(f"\n发送人：{message.author.username}\n发送内容：{message.content}")
        # await message.reply(content=f"机器人{self.robot.name}收到你的@消息了: {message.content}")
        if message.content == "" or "/" not in message.content:
            return
        # await modules.simple_reply.execute.Execute(self, message)
        if "/Search" in message.content:
            await modules.resonance.search.Search(self, message)
        elif "/Repor" in message.content:
            await modules.resonance.report.Report(self, message)
        return


if __name__ == "__main__":
    # 通过预设置的类型，设置需要监听的事件通道
    # intents = botpy.Intents.none()
    # intents.public_guild_messages=True

    # 通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents(public_guild_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=CONFIG["appid"], secret=CONFIG["secret"])
