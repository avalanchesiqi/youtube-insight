#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Example to illustrate the usage of youtube_insight crawler.
"""

import sys, os, argparse, json, logging

from youtube_insight.crawler import Crawler


if __name__ == '__main__':
    # == == == == == == == == Part 1: Read video ids from file == == == == == == == == #
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input file path of video ids or channel ids', required=True)
    parser.add_argument('-o', '--output', help='output file path of video data or channel video list', required=True)
    parser.add_argument('-c', '--channel', dest='channel', action='store_true', default=False)
    parser.add_argument('-r', '--relevant',  dest='relevant', action='store_true', default=False)
    parser.set_defaults(channel=False)
    parser.set_defaults(relevant=False)
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    logging.basicConfig(filename='./youtube_insight_crawler.log', level=logging.WARNING)

    if not os.path.exists(input_path):
        print('>>> Input file does not exist!')
        print('>>> Exit...')
        sys.exit(1)

    crawled_ids = set()
    if os.path.exists(output_path):
        print('>>> Output file already exists, append to current file...')
        is_channel = False
        is_video = False
        with open(output_path, 'r') as fin:
            for line in fin:
                obj_json = json.loads(line.rstrip())
                if is_channel:
                    crawled_ids.add(obj_json['channelId'])
                elif is_video:
                    crawled_ids.add(obj_json['id'])
                elif 'channelId' in obj_json:
                    crawled_ids.add(obj_json['channelId'])
                    is_channel = True
                elif 'id' in obj_json:
                    crawled_ids.add(obj_json['id'])
                    is_video = True
        output_data = open(output_path, 'a+')
    else:
        print('>>> Output file does not exist, start a new file...')
        output_data = open(output_path, 'w+')

    # == == == == == == == == Part 2: Set up crawler == == == == == == == == #
    d_key = 'Set your own developer key!'
    parts = 'snippet,contentDetails,statistics,topicDetails'
    fields = 'items(id,' \
             'snippet(publishedAt,channelId,title,description,thumbnails,channelTitle,categoryId,tags,defaultLanguage,defaultAudioLanguage),' \
             'contentDetails(duration,definition,caption,licensedContent,regionRestriction),' \
             'statistics,' \
             'topicDetails)'

    insight_crawler = Crawler()
    insight_crawler.set_key(d_key)
    insight_crawler.set_parts(parts)
    insight_crawler.set_fields(fields)

    # == == == == == == == == Part 3: Start crawler == == == == == == == == #
    # read the input file, start the crawler
    with open(input_path, 'r') as input_data:
        if args.channel:
            logging.info('>>> Crawling video ids for channels...')
            for cid in input_data:
                cid = cid.rstrip()
                if cid not in crawled_ids:
                    channel_data = insight_crawler.crawl_channel_vids(cid)
                    if channel_data is not None:
                        output_data.write('{0}\n'.format(json.dumps(channel_data)))
                        logging.info('--- Channel data crawler succeeded for channel: {0}'.format(cid))
                    else:
                        logging.error('--- Channel data crawler failed for channel: {0}'.format(cid))
        else:
            logging.info('>>> Crawling insight data for videos...')
            for vid in input_data:
                vid = vid.rstrip()
                if vid not in crawled_ids:
                    video_data = insight_crawler.crawl_insight_data(vid, args.relevant)
                    if video_data is not None:
                        output_data.write('{0}\n'.format(json.dumps(video_data)))
                        logging.info('--- Insight data crawler succeeded for video {0}'.format(vid))
                    else:
                        logging.error('--- Insight data crawler failed for video {0}'.format(vid))

    output_data.close()
