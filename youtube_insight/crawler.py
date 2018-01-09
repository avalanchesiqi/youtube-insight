import re, time, json, random, datetime, logging
from xml.etree import ElementTree

from youtube_insight import BaseCrawler


class Crawler(BaseCrawler):
    # Metadata crawler
    def list_video_metadata(self, video_id):
        """ Call API's videos.list method to list the video metadata. """
        for i in range(0, 5):
            try:
                response = self.crawler.videos().list(part=self.parts, fields=self.fields, id=video_id).execute()
                json_doc = response['items'][0]
                return json_doc
            except:
                time.sleep((2 ** i) + random.random())
        print('metadata crawler fails')

    # Insight data crawler
    def _parse_xml(self, xml_string):
        tree = ElementTree.fromstring(xml_string)
        graph_data = tree.find('graph_data')

        if graph_data is None:
            raise Exception('can not find data in the xml response')

        json_data = json.loads(graph_data.text)

        # try parse daily view count
        try:
            daily_view = json_data['views']['daily']['data']
        except KeyError:
            raise Exception('can not get view count in the xml response')

        # get start date
        start_date = datetime.date(1970, 1, 1) + datetime.timedelta(json_data['day']['data'][0] / 86400000)
        start_date = start_date.strftime("%Y-%m-%d")

        # get days with stats
        days = [(d - json_data['day']['data'][0]) / 86400000 for d in json_data['day']['data']]
        days = ','.join(map(str, days))

        # get total views
        try:
            total_view = json_data['views']['cumulative']['data'][-1]
        except:
            total_view = sum(daily_view)
        daily_view = ','.join(map(str, daily_view))

        # try parse daily share count and get total shares
        try:
            daily_share = json_data['shares']['daily']['data']
            try:
                total_share = json_data['shares']['cumulative']['data'][-1]
            except:
                total_share = sum(daily_share)
            daily_share = ','.join(map(str, daily_share))
        except:
            daily_share = 'N'
            total_share = 'N'

        # try parse daily watch time and get average watch time at the end
        try:
            daily_watch = json_data['watch-time']['daily']['data']
            try:
                avg_watch = 1.0 * json_data['watch-time']['cumulative']['data'][-1] / total_view
            except:
                avg_watch = 1.0 * sum(daily_watch) / total_view
            daily_watch = ','.join(map(str, daily_watch))
        except:
            daily_watch = 'N'
            avg_watch = 'N'

        # try parse daily subscriber count and get total subscribers
        try:
            daily_subscriber = json_data['subscribers']['daily']['data']
            try:
                total_subscriber = json_data['subscribers']['cumulative']['data'][-1]
            except:
                total_subscriber = sum(daily_subscriber)
            daily_subscriber = ','.join(map(str, daily_subscriber))
        except:
            daily_subscriber = 'N'
            total_subscriber = 'N'

        return '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\n'\
            .format(start_date, days, daily_view, total_view, daily_share, total_share,
                    daily_watch, avg_watch, daily_subscriber, total_subscriber)

    def request(self, vid):
        """Make a request to YouTube server to get historical data."""
        url = self.get_url(vid)
        header = self._get_header(self.cookie, vid)
        self.opener.addheaders = header

        time.sleep(random.uniform(0.1, 1))

        try:
            response = self.opener.open(url, self.post_data, timeout=5)
        except:
            logging.error('Video historical crawler: {0} server is down, can not get response, retry...'.format(vid))
            return 1, None

        try:
            content = response.read()
        except:
            logging.error('Video historical crawler: {0} response read time out, retry...'.format(vid))
            return 2, None

        try:
            csvstring = self._parse_xml(content)
        except:
            logging.error('Video historical crawler: {0} corrupted or empty xml, skip...'.format(vid))
            return 3, None

        return 0, csvstring