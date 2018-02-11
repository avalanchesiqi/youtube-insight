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

    def crawl_insight_data(self, video_id, relevant=False):
        """ Crawl youtube insight data.
        It returns a json object with fields set as self.fields, an example would be
        {id: ,
         snippet: {publishedAt: ,
                   channelId: ,
                   title: ,
                   description: ,
                   thumbnails: {},
                   channelTitle: ,
                   categoryId: ,
                   tags: [],
                   defaultLanguage: ,
                   defaultAudioLanguage: },
         statistics: {commentCount: ,
                      viewCount: ,
                      favoriteCount: ,
                      dislikeCount: ,
                      likeCount: },
         topicDetails: {topicIds: ,
                        relevantTopicIds: },
         contentDetails: {duration: ,
                          definition: ,
                          caption: ,
                          licensedContent: ,
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
                    totalSubscriber: },
        relevantVideos: [vid1, vid2, ...]
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
            if relevant:
                relevant_json = self.search_relevant_videos(video_id)
                if len(relevant_json) > 0:
                    insight_json.update({'relevantVideos': relevant_json})
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
                # remove the unnecessary part in thumbnail
                metadata_json['snippet']['thumbnails'] = metadata_json['snippet']['thumbnails']['default']['url']
                return metadata_json
            except Exception as e:
                logging.error('--- Exception in metadata crawler:', str(e))
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
                content = response.read().decode('utf-8')
                break
            except Exception as e:
                logging.error('--- Exception in historical data crawler:', str(e))
                continue

        try:
            historical_json = self._parse_xml(content)
            return historical_json
        except:
            return None

    def search_relevant_videos(self, video_id, page_token=None):
        """Find the relevant videos.
        """
        try:
            response = self.client.search().list(relatedToVideoId=video_id,  part='snippet', type='video',
                                                 order='relevance', maxResults=50, pageToken=page_token).execute()
            relevant_videos = []
            for metadata_json in response['items']:
                # extract relevant video ids
                relevant_videos.append(metadata_json['id']['videoId'])

            # recursively request next page
            if 'nextPageToken' in response:
                next_page_token = response['nextPageToken']
                relevant_videos.extend(self.search_relevant_videos(video_id, page_token=next_page_token))
            return relevant_videos
        except Exception as e:
            logging.error('--- Relevant videos crawler failed on video {0}: {1}'.format(video_id, str(e)))
