from modules.message_info import MessageInfo


class BaseHandle(object):
    async def HandleMessage(self, message_info: MessageInfo):
        pass

    def UpdateCheck(self) -> str:
        return None
