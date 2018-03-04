"""
Detect existence of verified badge on webpage to get channel status.
"""

import argparse, requests, logging
from bs4 import BeautifulSoup


def is_verified(channel_id):
    featured_page = 'https://www.youtube.com/channel/{0}/featured'.format(channel_id)
    try:
        r = requests.get(featured_page)
        soup = BeautifulSoup(r.text, 'lxml')
        for a in soup.find_all('a'):
            if not (a and a.get('href')):
                continue
            url = a.get('href')
            if 'support.google.com/youtube/answer/3046484?hl=en' in url:
                return True
    except Exception as e:
        logging.ERROR('{0} with msg {1}'.format(channel_id, str(e)))
    return False


def test_verified():
    # a verified channel: AdeleVEVO
    assert is_verified('UComP_epzeKzvBX156r6pm1Q') is True
    # a non-verified channel: YouLoveNeonVEVO
    assert is_verified('UC0MV27EmtpE0XsAl0jo9KYQ') is False


def start_query(input_path, output_data, verbose=False):
    with open(input_path, 'r') as fin:
        for line in fin:
            cid = line.rstrip()
            if is_verified(cid):
                output_data.write('{0}\n'.format(cid))
                if verbose:
                    print(cid, True)
            elif verbose:
                print(cid, False)


if __name__ == '__main__':
    # == == == == == == == == Part 1: Set up environment == == == == == == == == #
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input file of channel ids', required=True)
    parser.add_argument('-o', '--output', help='output file of verified channel ids', required=True)
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False)
    parser.set_defaults(verbose=False)
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    verbose = args.verbose
    logging.basicConfig(filename='./channel_status.log', level=logging.DEBUG)

    # == == == == == == == == Part 2: Verify candidate channel ids == == == == == == == == #
    output_data = open(output_path, 'w')
    # verify YouTube channel badge
    start_query(input_path, output_data, verbose)
    output_data.close()
