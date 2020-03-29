import unittest
import re
import collections
import sys
import datetime
from enum import Enum
import time

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
        self.result = dict.fromkeys([
                'FastestPage', 'MostActiveClient',
                'MostActiveClientByDay', 'MostPopularBrowser',
                'MostPopularPage', 'SlowestAveragePage', 'SlowestPage'
                ], ''
                )
        self.least_time = 0
        self.greatest_time = sys.maxsize * 2 + 1
        self.frequencyPage = {}
        self.fullTime = {}
        self.frequencyClient = {}
        self.frequencyBrowser = {}
        self.maximumAverageTime = 0
        self.dates = {}
        self.byDays = {}
        self.popularByDay = {}
        self.activeClientValue = 0
        self.popularPageValue = 0
        self.popularBrowserValue = 0
        self.mostActiveByDayValue = {}

    def add_line(self, line):
        if re.match(reg, line) is not None:
            data = reg.search(line)
            if (data.group('page') != '*'):
                self.update_stat(data)

    def update_stat(self, data):
        ip = data.group('ip')
        page = data.group('page')
        dateList = data.group('date').split('/')
        try:
            date = datetime.date(
                    int(dateList[2]), Months[dateList[1]].value,
                    int(dateList[0])
                    )
        except ValueError:
            return
        browser = data.group('browser')
        timeWork = int(data.group('time'))
        self.slowestPage(timeWork, page)
        self.fastestPage(timeWork, page)
        self.mostPopularPage(page)
        self.slowestAveragePage(timeWork, page)
        self.mostActiveClient(ip)
        self.mostPopularBrowser(browser)
        self.mostActiveClientByDay(ip, date)

    def slowestPage(self, time, page):
        if time >= self.least_time:
            self.result['SlowestPage'] = page
            self.least_time = time

    def fastestPage(self, time, page):
        if time <= self.greatest_time:
            self.result['FastestPage'] = page
            self.greatest_time = time

    def slowestAveragePage(self, time, page):
        if page in self.fullTime:
            self.fullTime[page] += time
        else:
            self.fullTime[page] = time
        fullTime = self.fullTime[page]
        frequency = self.frequencyPage[page]
        if self.result['SlowestAveragePage'] == page:
            self.maximumAverageTime = fullTime / frequency
            return
        if fullTime / frequency > self.maximumAverageTime:
            self.maximumAverageTime = fullTime / frequency
            self.result['SlowestAveragePage'] = page

    def mostActiveClient(self, ip):
        if ip in self.frequencyClient:
            self.frequencyClient[ip] += 1
        else:
            self.frequencyClient[ip] = 1
        if self.frequencyClient[ip] == self.activeClientValue:
            self.result['MostActiveClient'] = ip
            self.activeClientValue = self.frequencyClient[ip]
        if self.frequencyClient[ip] > self.activeClientValue:
            self.result['MostActiveClient'] = ip
            self.activeClientValue = self.frequencyClient[ip]

    def mostPopularPage(self, page):
        if page in self.frequencyPage:
            self.frequencyPage[page] += 1
        else:
            self.frequencyPage[page] = 1
        if self.frequencyPage[page] == self.popularPageValue:
            if page < self.result['MostPopularPage']:
                self.result['MostPopularPage'] = page
                self.popularPageValue = self.frequencyPage[page]
        if self.frequencyPage[page] > self.popularPageValue:
            self.result['MostPopularPage'] = page
            self.popularPageValue = self.frequencyPage[page]

    def mostPopularBrowser(self, browser):
        if browser in self.frequencyBrowser:
            self.frequencyBrowser[browser] += 1
        else:
            self.frequencyBrowser[browser] = 1
        if self.frequencyBrowser[browser] == self.popularBrowserValue:
            if browser < self.result['MostPopularBrowser']:
                self.result['MostPopularBrowser'] = browser
                self.popularBrowserValue = self.frequencyBrowser[browser]
        if self.frequencyBrowser[browser] > self.popularBrowserValue:
            self.result['MostPopularBrowser'] = browser
            self.popularBrowserValue = self.frequencyBrowser[browser]

    def mostActiveClientByDay(self, ip, date):
        if date in self.dates:
            if ip in self.dates[date]:
                self.dates[date][ip] += 1
            else:
                self.dates[date][ip] = 1
        else:
            self.dates[date] = {}
            self.dates[date][ip] = 1
            self.mostActiveByDayValue[date] = 0
        if self.dates[date][ip] == self.mostActiveByDayValue[date]:
            if ip < self.result['MostActiveClientByDay'][date]:
                self.byDays[date] = ip
                self.mostActiveByDayValue[date] = self.dates[date][ip]
        if self.dates[date][ip] > self.mostActiveByDayValue[date]:
            self.byDays[date] = ip
            self.mostActiveByDayValue[date] = self.dates[date][ip]
        self.result['MostActiveClientByDay'] = self.byDays

    def results(self):
        return self.result


def make_stat():
    # TODO: make your class instance and return it
    return LogsStat()


class LogStatTests(unittest.TestCase):
    # TODO: add unit tests
    def setUp(self):
        self.logsStat = make_stat()

    def tearDown(self):
        print('Русские Вперед!')

    def test_emptyLine(self):
        emptyLine = ''
        self.logsStat.add_line(emptyLine)
        self.assertDictEqual(self.logsStat.results(), {
            'FastestPage': '',
            'MostActiveClient': '',
            'MostActiveClientByDay': '',
            'MostPopularBrowser': '',
            'MostPopularPage': '',
            'SlowestAveragePage': '',
            'SlowestPage': ''
            })

    def test_wrongLine(self):
        wrongLine = '412fsdVGSVvds'
        self.logsStat.add_line(wrongLine)
        self.assertDictEqual(self.logsStat.results(), {
            'FastestPage': '',
            'MostActiveClient': '',
            'MostActiveClientByDay': '',
            'MostPopularBrowser': '',
            'MostPopularPage': '',
            'SlowestAveragePage': '',
            'SlowestPage': ''
            })

    def test_optionLine(self):
        optionLine = '''127.0.0.1 - - [08/Jul/2012:06:27:38 +0600]
        "OPTIONS * HTTP/1.0" 200 152 "-" "Apache/2.2.16 (Debian)
        (internal dummy connection)" 52'''
        self.logsStat.add_line(optionLine)
        self.assertDictEqual(self.logsStat.results(), {
            'FastestPage': '',
            'MostActiveClient': '',
            'MostActiveClientByDay': '',
            'MostPopularBrowser': '',
            'MostPopularPage': '',
            'SlowestAveragePage': '',
            'SlowestPage': ''
            })

    def test_wrongDate(self):
        line = '''192.168.12.155 - - [88/Jul/2012:06:27:46 +0600]
       "GET /js/script.js HTTP/1.1" 304 212 "http://callider/menu-top.php"
       "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0;
       SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729;
       Media Center PC 6.0; Tablet PC 2.0; .NET4.0C; .NET4.0E; InfoPath.3;
       MS-RTC LM 8)" 1793'''
        self.logsStat.add_line(line)
        self.assertDictEqual(self.logsStat.results(), {
            'FastestPage': '',
            'MostActiveClient': '',
            'MostActiveClientByDay': '',
            'MostPopularBrowser': '',
            'MostPopularPage': '',
            'SlowestAveragePage': '',
            'SlowestPage': ''
            })
