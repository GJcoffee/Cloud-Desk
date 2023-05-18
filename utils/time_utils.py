import datetime
import time
from datetime import date, timedelta


class DateUtils(object):

    @staticmethod
    def get_format_date(n_day=1, date_format="%Y-%m-%d"):
        """
        生成n_day前的时间年月日，格式2021-04-06
        :param n_day:
         :param date_format: 日期格式
        :return:
        """
        return (date.today() - timedelta(days=n_day)).strftime(date_format)

    @staticmethod
    def get_current_format_time(date_format="%Y-%m-%d %H:%M:%S"):
        """
        格式化当前时间
        :param date_format:
        :return:
        """
        return time.strftime(date_format, time.localtime(time.time()))

    @staticmethod
    def check_date(date_str, date_format="%Y-%m-%d"):
        """
        判断日期格式是否匹配
        :param date_str:
        :param date_format: 日期格式 %Y-%m-%d， %Y%m%d
        :return:
        """
        try:
            time.strptime(date_str, date_format)
            return True
        except:
            return False

    @staticmethod
    def cal_date(small_date, big_date, date_format="%Y-%m-%d"):
        """
        计算日期差的天数
        :param small_date: 前面日期
        :param big_date: 大后面日期
        :param date_format: 日期格式 %Y-%m-%d， %Y%m%d
        :return:
        """
        small_date = time.strptime(small_date, date_format)
        big_date = time.strptime(big_date, date_format)
        small_date = datetime.datetime(small_date[0], small_date[1], small_date[2])
        big_date = datetime.datetime(big_date[0], big_date[1], big_date[2])
        return (big_date - small_date).days

    @staticmethod
    def check_less_than_yesterday(date_str):
        """
        检查日期是否小于今天
        :param date_str:
        :return:
        """
        format_str = "%Y-%m-%d"
        if DateUtils.check_date(date_str, "%Y%m%d"):
            format_str = "%Y%m%d"
        return DateUtils.cal_date(date_str, DateUtils.get_format_date(date_format=format_str),
                                  date_format=format_str) >= 0
