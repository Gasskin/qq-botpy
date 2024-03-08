from modules import utils as g_utils
from modules.resonance import utils as r_utils


class ReportInfo(object):
    pre_report_time: float = 0.0  # 上一次上报的时间
    pre_percentage: float = 100.0  # 上一次上报的百分比
    report_time: float = 0.0  # 上报时间
    percentage: float = 100.0  # 百分比

    def Refresh(self, percentage: float, report_time: float) -> None:
        self.pre_report_time = self.report_time
        self.pre_percentage = self.percentage

        self.percentage = percentage
        self.report_time = report_time

    def Back(self):
        self.percentage = self.pre_percentage
        self.report_time = self.pre_report_time

    def GetValid(self) -> str:
        now = g_utils.GetCurrentSecondTimeStamp()
        if now - self.report_time < 600:
            valid = "(有效)"
        elif now - self.report_time < 3600:
            valid = "(未知)"
        else:
            valid = "(失效)"
        return valid

    def GetValidValue(self) -> str:
        now = g_utils.GetCurrentSecondTimeStamp()
        if now - self.report_time < 600:
            valid = 1
        elif now - self.report_time < 3600:
            valid = 0.5
        else:
            valid = 0
        return valid


class ReportInfos(object):
    # 商品/城市/上报信息
    reports: "dict[int, dict[int, ReportInfo]]"

    def __init__(self) -> None:
        self.reports = {}
        return

    def Refresh(self, item_id: int, city_id: int, percentage: float, report_time: float):
        if item_id not in self.reports:
            self.reports[item_id] = {}
        if city_id not in self.reports[item_id]:
            self.reports[item_id][city_id] = ReportInfo()
        self.reports[item_id][city_id].Refresh(percentage, report_time)

    def GetAndAddDefaultIfNone(self, item_id, city_id) -> ReportInfo:
        flag = False
        if item_id not in self.reports:
            self.reports[item_id] = {}
            flag = True
        if city_id not in self.reports[item_id]:
            self.reports[item_id][city_id] = ReportInfo()
            flag = True
        if flag:
            self.reports[item_id][city_id].Refresh(100.0, 0)
        return self.reports[item_id][city_id]
