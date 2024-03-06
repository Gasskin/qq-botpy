from datetime import datetime


class Report(object):
    # 上报时间
    report_time = 0
    # 上报的商品ID
    report_id = 0
    # 上报的城市
    report_city = 0
    # 上报的市场百分比
    report_percentage = 0

    def __init__(self) -> None:
        self.report_time = datetime.timestamp(datetime.now())
        return
