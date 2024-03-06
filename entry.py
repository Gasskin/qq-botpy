import asyncio
import os
from datetime import datetime
import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import Message

import modules.resonance.search
import modules.resonance.report
import modules.resonance.recommend

_log = logging.get_logger()

# 配置
CONFIG = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

Interval = {}

WhiteId = {"9631977870258360057": True}


class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_at_message_create(self, message: Message):
        _log.info(
            f"\n发送人：{message.author.username} {message.author.id}\n发送内容：{message.content}"
        )

        if message.author.id not in WhiteId:
            now = datetime.timestamp(datetime.now())
            if message.author.id not in Interval:
                Interval[message.author.id] = now
            elif Interval[message.author.id] - now <= 30:
                _log.info("发送消息过于频繁")
                return

        if message.content == "" or "/" not in message.content:
            return
        elif "/Search" in message.content:
            await modules.resonance.search.Search(self, message)
        elif "/Report" in message.content:
            await modules.resonance.report.Report(self, message)
        elif "/Recommend" in message.content:
            return
        return


if __name__ == "__main__":
    # 通过预设置的类型，设置需要监听的事件通道
    # intents = botpy.Intents.none()
    # intents.public_guild_messages=True

    # 通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents(public_guild_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=CONFIG["appid"], secret=CONFIG["secret"])
