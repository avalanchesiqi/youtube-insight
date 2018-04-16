# -*- coding: utf-8 -*-
"""
This is the main class of youtube_insight crawler.
It crawls metadata from YouTube V3 API and historical data from web request.
"""

import time, random, logging

from youtube_insight import BaseCrawler


class Crawler(BaseCrawler):
    def __init__(self):
        super(Crawler, self).__init__()

    def crawl_insight_data(self, video_id):
        """ Crawl youtube insight data.
        It returns a json object with fields set as self.fields, an example would be
        {id: ,
         snippet: {publishedAt: ,
                   channelId: ,
                   title: ,
                   description: ,
                   channelTitle: ,
                   categoryId: ,
                   tags: },
         statistics: {commentCount: ,
                      viewCount: ,
                      favoriteCount: ,
                      dislikeCount: ,
                      likeCount: },
         topicDetails: {topicIds: ,
                        relevantTopicIds: },
         contentDetails: {duration: ,
                          dimension: ,
                          definition: ,
                          caption: ,
                          regionRestriction: },
         insights: {startDate: ,
                    days: ,
                    dailyView: ,
                    totalView: ,
                    dailyShare: ,
                    totalShare: ,
                    dailyWatch: ,
                    avgWatch: ,
                    dailySubscriber: ,
                    totalSubscriber: }
        }

        note:
        1. insights field will not exist if historical data crawler fails
        2. insights may have missing keys if those fields are unavailable fields
        """
        insight_json = self.crawl_metadata(video_id)
        if insight_json is not None:
            historical_json = self.crawl_historical_data(video_id)
            if historical_json is not None:
                insight_json.update({'insights': historical_json})
            return insight_json
        return None

    def crawl_metadata(self, video_id):
        """ Call API's videos.list method to list video metadata.
        """
        # exponential back-off
        for i in range(0, 3):
            try:
                response = self.client.videos().list(id=video_id, part=self.parts, fields=self.fields).execute()
                metadata_json = response['items'][0]
                return metadata_json
            except Exception as e:
                print(e)
                time.sleep((2 ** i) + random.random())
        logging.error('--- Metadata crawler failed on video {0}'.format(video_id))
        return None

    def crawl_historical_data(self, video_id):
        """ Make a request to YouTube server to get historical data.
        """
        url = self.get_url(video_id)
        header = self._get_header(self.cookie, video_id)
        self.opener.addheaders = header
        content = None

        # exponential back-off
        for i in range(1, 4):
            time.sleep(random.uniform(0.1, 1))
            try:
                response = self.opener.open(url, self.post_data, timeout=2**i)
                content = response.read()
                break
            except:
                continue

        try:
            historical_json = self._parse_xml(content)
            return historical_json
        except:
            return None

    def crawl_playlist(self, channelId):
        """ Call API's playlists().list method to playlists.
        """
        return self.client.playlists().list(channelId=channelId, part=self.parts, maxResults=self.maxResults).execute()

    def crawl_playlist_items(self, playlistId):
        """ Call API's playlistItems().list method to playlists.
        """
        return self.client.playlistItems().list(playlistId=playlistId, part=self.parts, maxResults=self.maxResults).execute()
