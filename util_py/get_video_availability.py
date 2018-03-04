"""
Detect availability of a list of videos on webpage, this includes existence of video and historical attention series.
"""

import argparse, requests, logging
from bs4 import BeautifulSoup


def is_available(video_id):
    video_page = 'https://www.youtube.com/watch?v={0}'.format(video_id)
    try:
        r = requests.get(video_page)
        soup = BeautifulSoup(r.text, 'lxml')
        for s in soup.find_all('span', {'class': 'yt-ui-menu-item-label'}):
            if not (s and s.string):
                continue
            if s.string == 'Statistics':
                return True
    except Exception as e:
        logging.ERROR('{0} with msg {1}'.format(video_id, str(e)))
    return False


def test_availability():
    # an available video: Adele - Hello
    assert is_available('YQHsXMglC9A') is True
    # an unavailable video: How To Service Cartridge Bearings On Your Road Bike
    assert is_available('nxBWBT2lmR8') is False


def start_query(input_path, output_data, verbose=False):
    with open(input_path, 'r') as fin:
        for line in fin:
            vid = line.rstrip()
            if is_available(vid):
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

    # == == == == == == == == Part 2: Verify candidate channel ids == == == == == == == == #
    output_data = open(output_path, 'w', buffering=0)
    # get availability of YouTube videos
    start_query(input_path, output_data, verbose)
    output_data.close()
