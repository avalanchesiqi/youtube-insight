# -*- coding: utf-8 -*-
"""
This is the main class of youtube_insight crawler.
It crawls metadata from YouTube V3 API and historical data from web request.
"""

import time, random, logging
from langdetect import detect

from youtube_insight import BaseCrawler


class Crawler(BaseCrawler):
    def __init__(self):
        super(Crawler, self).__init__()

    def crawl_channel_vids(self, channel_id):
        """ Crawl channel video id list.
        It returns a json object that lists channel snippet and current videos, an example would be
        {channelId: ,
         snippet: {publishedAt: ,
                   description: ,
                   thumbnails: ,
                   title: },
         statistics: {viewCount: ,
                      commentCount: ,
                      subscriberCount: ,
                      hiddenSubscriberCount: ,
                      videoCount: },
        channelVideos: [vid1, vid2, ...]
        }
        """
        channel_json = self.list_channel_statistics(channel_id)
        if channel_json is not None:
            channel_videos_list = self.list_channel_videos(channel_id)
            if len(channel_videos_list) > 0:
                channel_json.update({'channelVideos': channel_videos_list})
            return channel_json
        return None

    def list_channel_statistics(self, channel_id):
        """ Call the API's channels().list method to list the existing channel statistics.
        """
        # exponential back-off
        for i in range(0, 3):
            try:
                response = self.client.channels().list(id=channel_id, part='snippet, statistics').execute()
                if response is not None and isinstance(response['items'], list) and len(response['items']) > 0:
                    res_json = response['items'][0]
                    channel_json = {'channelId': res_json['id'],
                                    'snippet': {'publishedAt': res_json['snippet']['publishedAt'],
                                                'description': res_json['snippet']['description'],
                                                'thumbnails': res_json['snippet']['thumbnails']['default']['url'],
                                                'title': res_json['snippet']['title']},
                                    'statistics': res_json['statistics']}
                    return channel_json
            except Exception as e:
                logging.error('--- Exception in channel statistics crawler:', str(e))
                time.sleep((2 ** i) + random.random())
        logging.error('--- Channel statistics crawler failed on channel {0}'.format(channel_id))
        return None

    def list_channel_videos(self, channel_id, page_token=None):
        """ Call the API's search().list method to list the existing channel video ids.
        """
        # exponential back-off
        for i in range(0, 3):
            try:
                response = self.client.search().list(channelId=channel_id, part='snippet', type='video',
                                                     order='date', maxResults=50, pageToken=page_token).execute()
                if response is not None and isinstance(response['items'], list) and len(response['items']) > 0:
                    channel_videos = []
                    for res_json in response['items']:
                        # extract channel video ids
                        channel_videos.append(res_json['id']['videoId'])

                    # recursively request next page
                    if 'nextPageToken' in response:
                        next_page_token = response['nextPageToken']
                        channel_videos.extend(self.list_channel_videos(channel_id, page_token=next_page_token))
                    return channel_videos
            except Exception as e:
                logging.error('--- Channel videos crawler failed on channel {0}: {1}'.format(channel_id, str(e)))
        return []

    def crawl_insight_data(self, video_id, relevant=False):
        """ Crawl youtube insight data.
        It returns a json object with fields set as self.fields, an example would be
        {id: ,
         snippet: {publishedAt: ,
                   channelId: ,
                   title: ,
                   description: ,
                   thumbnails: ,
                   channelTitle: ,
                   categoryId: ,
                   tags: [],
                   defaultLanguage/detectLanguage: ,
                   defaultAudioLanguage: },
         statistics: {viewCount: ,
                      commentCount: ,
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
                relevant_videos_list = self.search_relevant_videos(video_id)
                if len(relevant_videos_list) > 0:
                    insight_json.update({'relevantVideos': relevant_videos_list})
            return insight_json
        return None

    def crawl_metadata(self, video_id):
        """ Call API's videos().list method to list video metadata.
        """
        # exponential back-off
        for i in range(0, 3):
            try:
                response = self.client.videos().list(id=video_id, part=self.parts, fields=self.fields).execute()
                if response is not None and isinstance(response['items'], list) and len(response['items']) > 0:
                    res_json = response['items'][0]
                    # remove the unnecessary part in thumbnail
                    res_json['snippet']['thumbnails'] = res_json['snippet']['thumbnails']['default']['url']
                    # use langdetect if defaultLanguage not available
                    if 'defaultLanguage' not in res_json['snippet']:
                        try:
                            res_json['snippet']['detectLanguage'] = detect(res_json['snippet']['title'] + res_json['snippet']['description'])
                        except Exception:
                            pass
                    return res_json
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
            except OSError as e:
                logging.error('--- Socket timed out in historical data crawler:', str(e))
            except Exception as e:
                logging.error('--- Exception in historical data crawler:', str(e))
                continue

        try:
            historical_json = self._parse_xml(content)
            return historical_json
        except:
            return None

    def search_relevant_videos(self, video_id, page_token=None):
        """ Call API's search().list method to search the relevant videos.
        """
        relevant_videos = []
        try:
            response = self.client.search().list(relatedToVideoId=video_id,  part='snippet', type='video',
                                                 order='relevance', maxResults=50, pageToken=page_token).execute()
            if response is not None and isinstance(response['items'], list) and len(response['items']) > 0:
                for res_json in response['items']:
                    # extract relevant video ids
                    relevant_videos.append(res_json['id']['videoId'])

                # recursively request next page
                if 'nextPageToken' in response:
                    next_page_token = response['nextPageToken']
                    relevant_videos.extend(self.search_relevant_videos(video_id, page_token=next_page_token))
        except Exception as e:
            logging.error('--- Relevant videos crawler failed on video {0}: {1}'.format(video_id, str(e)))
        return relevant_videos
