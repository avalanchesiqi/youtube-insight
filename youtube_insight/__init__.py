import re, time, random, logging
import urllib, urllib2, cookielib
from apiclient import discovery


class BaseCrawler(object):
    # YouTube API service and version
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'

    def __init__(self):
        self.key = None
        self.parts = None
        self.fields = None
        self.crawler = None
        self.opener = urllib2.build_opener()
        self.cookie, self.session_token = self._get_cookie_and_sessiontoken()
        self.post_data = self.get_post_data(self.session_token)
        logging.basicConfig(filename='./youtube_crawler.log', level=logging.WARNING)

    @staticmethod
    def _get_cookie_and_sessiontoken():
        """Get cookie and sessiontoken."""
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), urllib2.HTTPHandler())
        req = urllib2.Request('https://www.youtube.com/watch?v=' + 'rYEDA3JcQqw')
        src = opener.open(req).read()

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
        """Get the session token."""
        return urllib.urlencode({'session_token': session_token})

    @staticmethod
    def get_url(vid):
        """Get the insight request URL."""
        return 'https://www.youtube.com/insight_ajax?action_get_statistics_and_data=1&v=' + vid

    @staticmethod
    def _get_header(cookie, vid):
        """Get the request header for historical data crawler."""
        headers = []
        headers.append(('Content-Type', 'application/x-www-form-urlencoded'))
        headers.append(('Cookie', cookie))
        headers.append(('Origin', 'https://www.youtube.com'))
        headers.append(('Referer', 'https://www.youtube.com/watch?v=' + vid))
        headers.append(('User-Agent',
                        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'))
        return headers

    def set_key(self, key):
        """ Set developer key. """
        self.key = key
        self.crawler = discovery.build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION, developerKey=self.key)

    def set_parts(self, parts):
        """ Target video parts. """
        self.parts = parts

    def set_fields(self, fields):
        """ Fine-grained crawler parts."""
        self.fields = fields
