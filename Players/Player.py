import abc

class Player:
    """An abstract sports player"""

    def __init__(self, player_id, profile_url, scraper):
        """
            Args:
                - player_id (int): Unique ID for player
                - profile_url (str): URL to the player's profile
                - scraper (obj): instance of Scraper class

            Returns:
                None
        """
        self.player_id = player_id
        self.profile_url = profile_url
        self.scraper = scraper
        self.seasons_with_stats = []
        self.game_stats = []

    @abc.abstractmethod
    def scrape_profile(self):
        """Scrape profile info for player"""
        raise Exception("Not Implemented")
        
    @abc.abstractmethod
    def scrape_player_stats(self):
        """Scrape the stats for all available games for a player"""
        raise Exception("Not Implemented")

    @abc.abstractmethod
    def scrape_season_gamelog(self, gamelog_url, year):
        raise Exception("Not Implemented")

    @abc.abstractmethod
    def get_seasons_with_stats(self, profile_soup):
        raise Exception("Not Implemented")
