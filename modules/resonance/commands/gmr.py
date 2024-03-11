from modules.message_info import MessageInfo
from modules.base_handle import BaseHandle
from modules.resonance import utils as r_utils
from modules.resonance.configs import city
import requests
import traceback
from botpy import logging

_log = logging.get_logger()


class GMR(BaseHandle):
    WHITE_ID: dict[str, bool] = {"9631977870258360057": True, "0": False}

    async def HandleMessage(self, m: MessageInfo):
        return
