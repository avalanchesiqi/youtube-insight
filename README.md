# YouTube-insight
## An integrated YouTube data crawler
YouTube-insight is a tool to crawl video metadata and historical data for YouTube videos.

####An simple example
```python
from __future__ import print_function
import json
from youtube_insight.crawler import Crawler

insight_crawler = Crawler()
d_key = 'Set your own developer key!'
parts = 'snippet,statistics,topicDetails,contentDetails'
insight_crawler.set_key(d_key)
insight_crawler.set_parts(parts)

vid = 'ITtlxjvLQis'
video_data = insight_crawler.crawl_insight_data(vid)
print(json.dumps(video_data, indent=4, sort_keys=True))
```