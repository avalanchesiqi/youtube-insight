import time, random
from apiclient import discovery
import logging


class Crawler:
    # YouTube API service and version
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'

    def __init__(self):
        self.key = None
        self.parts = None
        self.fields = None
        self.crawler = None

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

    def list_video_metadata(self, video_id):
        """ Call API's videos.list method to list the video metadata. """
        for i in xrange(0, 5):
            try:
                response = self.crawler.videos().list(part=self.parts, id=video_id, fields=self.fields).execute()
                json_doc = response['items'][0]
                return json_doc
            except:
                time.sleep((2 ** i) + random.random())
