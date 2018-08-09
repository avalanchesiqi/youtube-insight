# -*- coding: utf-8 -*-
"""
This is the base class of youtube_insight crawler.
It sets up a client to interact with API and an opener to send request from.
"""

import time, datetime, random, json, re, urllib
from http.cookiejar import CookieJar
from googleapiclient import discovery
from googletrans import Translator
from xml.etree import ElementTree

# YouTube API service and version
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


class BaseCrawler(object):
    def __init__(self):
        self.key = None
        self.parts = None
        self.fields = None
        self.client = None
        self.opener = urllib.request.build_opener()
        self.cookie, self.session_token = self._get_cookie_and_sessiontoken()
        self.post_data = self.get_post_data(self.session_token)
        self.translator = Translator()

    # == == == == == == == == methods to construct data api client == == == == == == == == #
    def set_key(self, key):
        """ Set developer key.
        """
        self.key = key
        self.client = discovery.build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                                      developerKey=self.key, cache_discovery=False)

    def set_parts(self, parts):
        """ Set target video parts.
        """
        self.parts = parts

    def set_fields(self, fields):
        """ Set fine-grained target video fields within parts.
        """
        self.fields = fields

    def update_translator(self):
        """ Update Google translator.
        """
        self.translator = Translator()

    # == == == == == == == == methods to construct historical data opener == == == == == == == == #
    @staticmethod
    def _get_cookie_and_sessiontoken():
        """ Get cookie and sessiontoken.
        """
        cj = CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPHandler())
        req = urllib.request.Request('https://www.youtube.com/watch?v=' + 'rYEDA3JcQqw')
        src = opener.open(req).read().decode('utf-8')

        time.sleep(random.random())

        cookiename = ['YSC', 'PREF', 'VISITOR_INFO1_LIVE', 'ACTIVITY']
        cookie = ''
        for cookie_i in cj:
            if cookie_i.name in cookiename:
                cookie += (cookie_i.name + '=' + cookie_i.value + '; ')
        cookie = cookie[0:-2]

        re_st = re.compile('\'XSRF_TOKEN\'\: \"([^\"]+)\"\,')
        session_token = re_st.findall(src)[0]
        return cookie, session_token

    @staticmethod
    def get_post_data(session_token):
        """ Get the session token.
        """
        return urllib.parse.urlencode({'session_token': session_token}).encode('utf-8')

    @staticmethod
    def get_url(vid):
        """ Get the historical data request URL.
        """
        return 'https://www.youtube.com/insight_ajax?action_get_statistics_and_data=1&v=' + vid

    @staticmethod
    def _get_header(cookie, vid):
        """ Get the request header for historical data crawler.
        """
        headers = []
        headers.append(('Content-Type', 'application/x-www-form-urlencoded'))
        headers.append(('Cookie', cookie))
        headers.append(('Origin', 'https://www.youtube.com'))
        headers.append(('Referer', 'https://www.youtube.com/watch?v=' + vid))
        headers.append(('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'))
        return headers

    # == == == == == == == == method to parse retrieved xml response == == == == == == == == #
    @staticmethod
    def _parse_xml(xml_string):
        """ Parse xml response from historical data crawler.
        """
        xml_tree = ElementTree.fromstring(xml_string)
        graph_data = xml_tree.find('graph_data')

        if graph_data is None:
            raise Exception('--- Can not find data in the xml response')

        json_data = json.loads(graph_data.text)
        json_return = {}

        # try parse daily view count
        try:
            daily_view = json_data['views']['daily']['data']
        except:
            raise Exception('-- Can not get view count in the xml response')
        json_return['dailyView'] = daily_view

        # get start date
        start_date = datetime.datetime.fromtimestamp(json_data['day']['data'][0]/1000.0)
        start_date = start_date.strftime('%Y-%m-%d')
        json_return['startDate'] = start_date

        # get days with stats
        days = [round((d - json_data['day']['data'][0]) / 86400000) for d in json_data['day']['data']]
        json_return['days'] = days

        # get total views
        total_view = sum(daily_view)
        json_return['totalView'] = total_view

        # try parse daily share count and get total shares
        if 'shares' in json_data:
            daily_share = json_data['shares']['daily']['data']
            total_share = sum(daily_share)
            json_return['dailyShare'] = daily_share
            json_return['totalShare'] = total_share

        # try parse daily watch time and get average watch time
        if 'watch-time' in json_data:
            daily_watch = json_data['watch-time']['daily']['data']
            avg_watch = sum(daily_watch) / total_view
            json_return['dailyWatch'] = daily_watch
            json_return['avgWatch'] = avg_watch

        # try parse daily subscriber count and get total subscribers
        if 'subscribers' in json_data:
            daily_subscriber = json_data['subscribers']['daily']['data']
            total_subscriber = sum(daily_subscriber)
            json_return['dailySubscriber'] = daily_subscriber
            json_return['totalSubscriber'] = total_subscriber

        return json_return
