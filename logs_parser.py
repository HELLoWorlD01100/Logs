import unittest
import re
import collections
import sys
import datetime
from enum import Enum

global reg
reg = re.compile(
            r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(?P<date>\d{2}'
            r'/(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)/\d{4}):\d{2}:'
            r'\d{2}:\d{2} \+\d{4}] "(GET|PUT|POST|HEAD|OPTIONS|DELETE) '
            r'(?P<page>\S+) \S+" \d+ \d+ "\S+" "(?P<browser>.+)"'
            r'( (?P<time>\d+)|)')


class Months(Enum):
    Jan = 1
    Feb = 2
    Mar = 3
    Apr = 4
    May = 5
    Jun = 6
    Jul = 7
    Aug = 8
    Sep = 9
    Oct = 10
    Nov = 11
    Dec = 12


class LogsStat:
    def __init__(self):
        self.result = dict.fromkeys(
            [
                'FastestPage', 'MostActiveClient',
                'MostActiveClientByDay', 'MostPopularBrowser',
                'MostPopularPage', 'SlowestAveragePage', 'SlowestPage'
            ]
        )
        self.least_time = 0
        self.greatest_time = sys.maxsize * 2 + 1
        self.frequencyPage = {}
        self.fullTime = {}
        self.frequencyClient = {}
        self.frequencyBrowser = {}
        self.maximum = 0
        self.dates = {}
        self.byDays = {}
        self.popularByDay = {}

    def add_line(self, line):
        if re.match(reg, line) is not None:
            data = reg.search(line)
            if (data.group('page') != '*'):
                self.update_stat(data)

    def update_stat(self, data):
        ip = data.group('ip')
        page = data.group('page')
        dateList = data.group('date').split('/')
        date = datetime.date(
            int(dateList[2]), Months[dateList[1]].value, int(dateList[0])
            )
        browser = data.group('browser')
        time = int(data.group('time'))
        self.slowestPage(time, page)
        self.fastestPage(time, page)
        self.slowestAveragePage(time, page)
        self.mostActiveClient(ip)
        self.mostPopularPage()
        self.mostPopularBrowser(browser)
        self.mostPopularClientByDay(ip, date)

    def slowestPage(self, time, page):
        if time >= self.least_time:
            self.result['SlowestPage'] = page
            self.least_time = time

    def fastestPage(self, time, page):
        if time <= self.greatest_time:
            self.result['FastestPage'] = page
            self.greatest_time = time

    def slowestAveragePage(self, time, page):
        if page in self.frequencyPage:
            self.frequencyPage[page] += 1
            self.fullTime[page] += time
        else:
            self.frequencyPage[page] = 1
            self.fullTime[page] = time
        if self.result['SlowestAveragePage'] == page:
            self.maximum = self.fullTime[page] / self.frequencyPage[page]
            return
        if self.fullTime[page] / self.frequencyPage[page] > self.maximum:
            self.maximum = self.fullTime[page] / self.frequencyPage[page]
            self.result['SlowestAveragePage'] = page

    def mostActiveClient(self, ip):
        if ip in self.frequencyClient:
            self.frequencyClient[ip] += 1
        else:
            self.frequencyClient[ip] = 1
        self.result['MostActiveClient'] = collections.Counter(sorted(
            collections.Counter(self.frequencyClient).elements())
            ).most_common()[0][0]

    def mostPopularPage(self):
        self.result['MostPopularPage'] = collections.Counter(sorted(
            collections.Counter(self.frequencyPage).elements())
            ).most_common()[0][0]

    def mostPopularBrowser(self, browser):
        if browser in self.frequencyBrowser:
            self.frequencyBrowser[browser] += 1
        else:
            self.frequencyBrowser[browser] = 1
        self.result['MostPopularBrowser'] = collections.Counter(sorted(
            collections.Counter(self.frequencyBrowser).elements())
            ).most_common()[0][0]

    def mostPopularClientByDay(self, ip, date):
        if date in self.dates:
            if ip in self.dates[date]:
                self.dates[date][ip] += 1
            else:
                self.dates[date][ip] = 1
        else:
            self.dates[date] = {}
        for key in self.dates:
            if self.dates[key]:
                self.byDays[key] = collections.Counter(sorted(
                    collections.Counter(self.dates[key]).elements())
                    ).most_common()[0][0]
        self.result['MostActiveClientByDay'] = self.byDays

    def results(self):
        return self.result


def make_stat():
    # TODO: make your class instance and return it
    return LogsStat()


class LogStatTests(unittest.TestCase):
    # TODO: add unit tests
    pass
