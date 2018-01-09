from __future__ import print_function
from youtube_insight.crawler import Crawler


if __name__ == '__main__':
    yt_crawler = Crawler()

    d_key = 'AIzaSyCmQaf0qnWl_PoSwtRedVsBN9EMicz4RpM'
    yt_crawler.set_key(d_key)
    yt_crawler.set_parts('snippet,statistics,topicDetails,contentDetails')

    vid = 'ITtlxjvLQis'
    # print(yt_crawler.list_video_metadata(video_id=vid))
    print(yt_crawler.request(vid))
