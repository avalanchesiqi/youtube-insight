"""
Detect availability of a list of videos on webpage, this includes existence of video and historical attention series.
We add an additional filter to select videos that published after 1 Jan, 2017.
"""

import argparse, requests, logging
from datetime import datetime
from bs4 import BeautifulSoup


def is_recent_available(video_id):
    video_page = 'https://www.youtube.com/watch?v={0}'.format(video_id)
    try:
        r = requests.get(video_page)
        soup = BeautifulSoup(r.text, 'lxml')
        d = soup.find('div', {'id': 'watch-uploader-info'})
        if not (d and d.text):
            return False
        # filter 1 on recency: must publish after 2017
        if datetime.strptime(d.text[-12:].lstrip(), '%b %d, %Y') > datetime.strptime('Dec 31, 2016', '%b %d, %Y'):
            for s in soup.find_all('span', {'class': 'yt-ui-menu-item-label'}):
                if not (s and s.string):
                    continue
                # filter 2 on availability: must contain historical attention series
                if s.string == 'Statistics':
                    return True
    except Exception as e:
        logging.exception('{0} with msg {1}'.format(video_id, str(e)))
    return False


def test_recent_available():
    # a recent and statistics available video: EXO 'Power' MV
    assert is_recent_available('sGRv8ZBLuW0') is True
    # a recent but statistics unavailable video: How To Service Cartridge Bearings On Your Road Bike
    assert is_recent_available('nxBWBT2lmR8') is False
    # a non-recent and statistics available video: Adele - Hello
    assert is_recent_available('YQHsXMglC9A') is False
    # a non-recent and statistics unavailable video: Road Bike Party 2 - Martyn Ashton
    assert is_recent_available('HhabgvIIXik') is False
    # a recent and statistics available streamed video: 24/7 Online KPOP IDOL Channel [ALL THE KPOP]
    assert is_recent_available('qGNyfwrjV0c') is True
    # a recent, statistics available and scheduled video: SEO Dominance Global
    assert is_recent_available('bb8X46CDt9I') is True


def start_query(input_path, output_data, verbose=False):
    with open(input_path, 'r') as fin:
        for line in fin:
            vid = line.rstrip()
            if is_recent_available(vid):
                output_data.write('{0}\n'.format(vid))
                if verbose:
                    print(vid, True)
            elif verbose:
                print(vid, False)


if __name__ == '__main__':
    # == == == == == == == == Part 1: Set up environment == == == == == == == == #
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input file of video ids', required=True)
    parser.add_argument('-o', '--output', help='output file of available video ids', required=True)
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False)
    parser.set_defaults(verbose=False)
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    verbose = args.verbose
    logging.basicConfig(filename='./video_recency_availability.log', level=logging.DEBUG)

    # == == == == == == == == Part 2: Get recent and statistics available video ids == == == == == == == == #
    output_data = open(output_path, 'w')
    # get availability of YouTube videos
    start_query(input_path, output_data, verbose)
    output_data.close()
