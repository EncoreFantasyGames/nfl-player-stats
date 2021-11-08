import string
from Scraper import Scraper

import sys
import os

BASE_URL = 'https://www.pro-football-reference.com{0}'
PLAYER_LIST_URL = 'https://www.pro-football-reference.com/players/{0}'
PLAYER_PROFILE_URL = 'https://www.pro-football-reference.com/players/{0}/{1}'
PLAYER_GAMELOG_URL = 'https://www.pro-football-reference.com/players/{0}/{1}/gamelog/{2}'

HEADERS = {
    'user-agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
                   '(KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36')
}

PROFILE_DIR = 'profile_data'
STATS_DIR = 'stats_data'

if __name__ == '__main__':
    letters_to_scrape = list(string.ascii_uppercase)
    if os.getenv("LETTERS") is not None:
        letters_to_scrape = list(os.getenv("LETTERS"))

    print("Beginning Scraping for letters: {}".format(letters_to_scrape))
    scraper = Scraper(profile_dir=PROFILE_DIR, stats_dir=STATS_DIR,
                          letters_to_scrape=letters_to_scrape, num_jobs=10, clear_old_data=False, sport="NFL",
                          headers=HEADERS, base_url=BASE_URL, player_list_url=PLAYER_LIST_URL,
                          player_profile_url=PLAYER_PROFILE_URL, player_gamelog_url=PLAYER_GAMELOG_URL)

    success, fail, total = scraper.scrape_site()
    print("Success: {0} = {2}\nFailure: {1} = {3}".format(success, fail, success/total, fail/total))


