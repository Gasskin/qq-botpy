from botpy.message import Message, DirectMessage
from modules import utils


class MessageInfo(object):
    author_id: str  # 发送人ID
    content: str  # 发送内容
    command: str  # 发送指令
    params: list[str]  # 参数列表
    send_time: float  # 发送时间
    message: Message  # 消息

    def __init__(self) -> None:
        return

    def InitWithMessage(self, message: Message):
        self.author_id = message.author.id
        self.content = message.content
        self.message = message
        self.send_time = utils.GetCurrentSecondTimeStamp()
        temp_params = message.content.split(" ")
        self.command = temp_params[1]
        self.params = []
        for i in range(2, len(temp_params)):
            self.params.append(temp_params[i])

    def InitWithDirectMessage(self, message: DirectMessage):
        self.author_id = message.author.id
        self.content = message.content
        self.message = message
        self.send_time = utils.GetCurrentSecondTimeStamp()
        temp_params = message.content.split(" ")
        self.command = temp_params[1]
        self.params = []
        for i in range(2, len(temp_params)):
            self.params.append(temp_params[i])
        pass
