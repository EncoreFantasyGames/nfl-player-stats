import requests
from multiprocessing.dummy import Pool
import time
import shutil
import json
import glob
from bs4 import BeautifulSoup

from Players.NFLPlayer import NFLPlayer
from Database import *


class Scraper:
    """Scraper for pro-football-reference.com to collect NFL player stats"""

    def __init__(self, profile_dir, stats_dir,
                 letters_to_scrape=['A'], num_jobs=1, clear_old_data=True, first_player_id=1, sport='NFL',
                 headers='', base_url='', player_list_url='',
                 player_profile_url='', player_gamelog_url=''):
        """Initialize the scraper to get player stats

                Args:
                    - letters_to_scrape (str[]): The site sorts players by the first letter of their
                      last name. This array tells the scraper which letters to scrape data for.
                    - num_jobs (int): Number of concurrent jobs the scraper should run. While Python
                      can't multi-thread, it can manage multiple processes at once, which allows it to
                      utilize time spent waiting for the server to respond.
                    - clear_old_data (boolean): Whether or not the data file should be wiped before
                      starting the scrape.
                    - first_player_id (int): The first ID for a player (set if you are rerunning to avoid duplicates)

                Returns:
                    None
        """
        # Data related to scraping jobs
        self.letters_to_scrape = [letter.upper() for letter in letters_to_scrape]
        self.num_jobs = num_jobs
        self.clear_old_data = clear_old_data
        self.session = requests.Session()
        self.start_time = time.time()
        self.cross_process_player_count = 0
        self.first_player_id = first_player_id

        # data related to output
        self.profile_dir = profile_dir
        self.stats_dir = stats_dir

        # data related to inputs and requests
        self.headers = headers
        self.base_url = base_url
        self.player_list_url = player_list_url
        self.player_profile_url = player_profile_url
        self.player_gamelog_url = player_gamelog_url
        self.sport = sport

        self.db = Database(db_name='encorefan', user='root', password='Ruben-5AW')
        if num_jobs > 1:
            self.multiprocessing = True
            self.worker_pool = Pool(num_jobs)
        else:
            self.multiprocessing = False

    def create_player_model(self, player_id, player_profile_url):
        if self.sport.upper() == "NFL":
            return NFLPlayer(player_id, player_profile_url, self)

    def scrape_site(self):
        """Pool workers to scrape players by first letter of last name"""
        if self.clear_old_data:
            self.clear_data()
        player_id = self.first_player_id
        for letter in self.letters_to_scrape:
            player_profile_urls = self.get_players_for_letter(letter)
            for player_profile_url in player_profile_urls:

                player = self.create_player_model(player_id, player_profile_url)
                try:
                    player.scrape_profile()
                    player.scrape_player_stats()
                except (KeyboardInterrupt, SystemExit):
                    raise
                except Exception as err:
                    print('There was a problem parsing stats for {} with error: {}'.format(player_profile_url, err))
                    continue
                self.save_player_profile(player.profile)
                self.save_player_game_stats(player.game_stats, player.player_id, player.profile['name'])
                player_id += 1
        #self.condense_data()

    def condense_data(self):
        """Condense data into two files, a profile file and a stats file"""
        print('Condensing Data...')
        condensed_profile_data = []
        all_profile_files = glob.glob('{}/*.json'.format(self.profile_dir))
        for file in all_profile_files:
            with open(file, 'rb') as fin:
                condensed_profile_data.append(json.load(fin))
        print('{} player profiles condensed'.format(len(condensed_profile_data)))
        filename = 'profiles_{}.json'.format(time.time())
        with open(filename, 'w') as fout:
            json.dump(condensed_profile_data, fout)

        condensed_game_data = []
        all_game_files = glob.glob('{}/*.json'.format(self.stats_dir))
        for file in all_game_files:
            with open(file, 'rb') as fin:
                condensed_game_data += json.load(fin)
        print('{} player seasons condensed'.format(len(condensed_game_data)))
        filename = 'games_{}.json'.format(time.time())
        with open(filename, 'w') as fout:
            json.dump(condensed_game_data, fout)

    def save_player_profile(self, profile):
        """
        Save a Player into table
        """
        self.db.insert_player(profile)
        

    def save_player_game_stats(self, games, player_id, player_name):
        """
        Save a list of player games with stats info
        """
        self.db.insert_game(games, player_id, player_name)

    def get_players_for_letter(self, letter):
        """
        Get a list of player links for a letter of the alphabet.
        """
        response = self.get_page(self.player_list_url.format(letter))
        soup = BeautifulSoup(response.content, 'html.parser')

        players = soup.find('div', {'id': 'div_players'}).find_all('a')
        return [self.base_url.format(players[0]['href'])]
        # return [self.base_url.format(player['href']) for player in players]

    def get_page(self, url, retry_count=0):
        """
        Use requests to get a page; retry when failures occur
        """
        try:
            return self.session.get(url, headers=self.headers)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            retry_count += 1
            if retry_count <= 3:
                self.session = requests.Session()
                return self.get_page(url, retry_count)
            else:
                raise

    def clear_data(self):
        """Clear the data directories"""
        try:
            shutil.rmtree(self.profile_dir)
        except FileNotFoundError:
            pass
        try:
            shutil.rmtree(self.stats_dir)
        except FileNotFoundError:
            pass