from bs4 import BeautifulSoup
import re

from Players.Player import Player


class NFLPlayer(Player):
    """
    An implementation of NFL Player model for scraping
    """
    def __init__(self, player_id, player_url, scraper):
        super().__init__(player_id, player_url, scraper)
        self.profile = self.generate_default_profile(player_id)

    def collect_soup(self, url):
        response = self.scraper.get_page(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

    @staticmethod
    def generate_default_profile(player_id):
        return {
            'player_id': player_id,
            'name': None,
            'position': None,
            'height': None,
            'weight': None,
            'current_team': None,
            'birth_date': None,
            'birth_place': None,
            'death_date': None,
            'college': None,
            'high_school': None,
            'draft_team': None,
            'draft_round': None,
            'draft_position': None,
            'draft_year': None,
            'current_salary': None,
            'hof_induction_year': None
        }

    @staticmethod
    def make_player_game_stats(player_id, year):
        """Factory method to return possible stats to collect for a player in a game

            Args:
                - player_id (int): unique Id for the player
                - year (int): The year the stats are for

            Returns:
                - game_stats (dict): dictionary with game stats initialized
        """
        return {
            'player_id': player_id,
            'year': year,
            # General stats
            'game_id': None,
            'date': None,
            'game_number': None,
            'age': None,
            'team': None,
            'game_location': None,
            'opponent': None,
            'game_won': None,
            'player_team_score': 0,
            'opponent_score': 0,
            # Passing stats
            'passing_attempts': 0,
            'passing_completions': 0,
            'passing_yards': 0,
            'passing_rating': 0,
            'passing_touchdowns': 0,
            'passing_interceptions': 0,
            'passing_sacks': 0,
            'passing_sacks_yards_lost': 0,
            # Rushing stats
            'rushing_attempts': 0,
            'rushing_yards': 0,
            'rushing_touchdowns': 0,
            # Receiving stats
            'receiving_targets': 0,
            'receiving_receptions': 0,
            'receiving_yards': 0,
            'receiving_touchdowns': 0,
            # Kick return stats
            'kick_return_attempts': 0,
            'kick_return_yards': 0,
            'kick_return_touchdowns': 0,
            # PUnt return stats
            'punt_return_attempts': 0,
            'punt_return_yards': 0,
            'punt_return_touchdowns': 0,
            # Defense
            'defense_sacks': 0,
            'defense_tackles': 0,
            'defense_tackle_assists': 0,
            'defense_interceptions': 0,
            'defense_interception_yards': 0,
            'defense_interception_touchdowns': 0,
            'defense_safeties': 0,
            # Kicking
            'point_after_attempts': 0,
            'point_after_makes': 0,
            'field_goal_attempts': 0,
            'field_goal_makes': 0,
            # Punting
            'punting_attempts': 0,
            'punting_yards': 0,
            'punting_blocked': 0
        }

    def scrape_profile(self):
        """
        Scrape profile section of webpage for an NFL player
        """
        soup = self.collect_soup(self.profile_url)

        profile_section = soup.find('div', {'id': 'meta'})
        self.profile['name'] = profile_section.find('h1', {'itemprop': 'name'}).contents[1].contents[0]
        self.profile['first_name'], self.profile['last_name'] = self.profile['name'].split(' ')

        profile_attributes = profile_section.find_all('p')
        current_attribute = 1
        num_attributes = len(profile_attributes)

        self.profile['position'] = profile_attributes[current_attribute].contents[2].split('\n')[0].split(' ')[1]
        current_attribute += 1

        height = profile_attributes[current_attribute].find('span', {'itemprop': 'height'})
        if height is not None:
            self.profile['height'] = height.contents[0]
        weight = profile_attributes[current_attribute].find('span', {'itemprop': 'weight'})
        if weight is not None:
            self.profile['weight'] = weight.contents[0].split('lb')[0]
        if height is not None or weight is not None:
            current_attribute += 1

        affiliation_section = profile_section.find('span', {'itemprop': 'affiliation'})
        if affiliation_section is not None:
            self.profile['current_team'] = affiliation_section.contents[0].contents[0]
            current_attribute += 1

        birth_date = profile_attributes[current_attribute].find('span', {'itemprop': 'birthDate'})
        if birth_date is not None:
            self.profile['birth_date'] = birth_date['data-birth']
        birth_place_section = profile_attributes[current_attribute].find('span', {'itemprop': 'birthPlace'}).contents
        try:
            self.profile['birth_place'] = re.split('\xa0', birth_place_section[0])[1] + ' ' + \
                                          birth_place_section[1].contents[0]
        except IndexError:
            pass
        if birth_date is not None or len(birth_place_section) > 0:
            current_attribute += 1

        death_section = profile_section.find('span', {'itemprop': 'deathDate'})
        if death_section is not None:
            self.profile['death_date'] = death_section['data-death']
            current_attribute += 1

        if profile_attributes[current_attribute].contents[0].contents[0] == 'College':
            self.profile['college'] = str(profile_attributes[current_attribute].contents[2].contents[0])
            current_attribute += 1

        # Skip weighted career AV
        current_attribute += 1

        if ((current_attribute + 1) <= num_attributes) and profile_attributes[current_attribute].contents[0].contents[
            0] == 'High School':
            self.profile['high_school'] = profile_attributes[current_attribute].contents[2].contents[0] + ', ' + \
                                          profile_attributes[current_attribute].contents[4].contents[0]
            current_attribute += 1

        if ((current_attribute + 1) <= num_attributes) and profile_attributes[current_attribute].contents[0].contents[
            0] == 'Draft':
            self.profile['draft_team'] = str(profile_attributes[current_attribute].contents[2].contents[0])
            draft_info = profile_attributes[current_attribute].contents[3].split(' ')
            self.profile['draft_round'] = re.findall(r'\d+', draft_info[3])[0]
            self.profile['draft_position'] = re.findall(r'\d+', draft_info[5])[0]
            self.profile['draft_year'] = \
                re.findall(r'\d+', profile_attributes[current_attribute].contents[4].contents[0])[0]
            current_attribute += 1

        if ((current_attribute + 1) <= num_attributes) and profile_attributes[current_attribute].contents[0].contents[
            0] == 'Current cap hit':
            profile_attributes[current_attribute].contents
            self.profile['current_salary'] = profile_attributes[current_attribute].contents[2].contents[0]
            current_attribute += 1

        if ((current_attribute + 1) <= num_attributes) and profile_attributes[current_attribute].contents[0].contents[
            0] == 'Hall of fame':
            self.profile['hof_induction_year'] = profile_attributes[current_attribute].contents[2].contents[0]
            current_attribute += 1

        self.profile['birth_city'], self.profile['birth_state'] = self.profile['birth_place'].split(', ')
        feet, inches = self.profile['height'].split('-')
        self.profile['height'] = int(feet)*12 + int(inches)
        self.seasons_with_stats = self.get_seasons_with_stats(soup)

    def get_seasons_with_stats(self, profile_soup):
        """Scrape a list of seasons that has stats for the player

            Args:
                - profile_soup (obj): The BeautifulSoup object for the player profile page

            Returns:
                - seasons (dict[]): List of dictionaries with meta information about season stats
        """
        seasons = []
        gamelog_list = profile_soup.find('div', {'id': 'inner_nav'}).find_all('li')[1].find_all('li')
        if len(gamelog_list) > 0 and gamelog_list[0].contents[0].contents[0] == 'Career':
            for season in gamelog_list:
                seasons.append({
                    'year': season.contents[0].contents[0],
                    'gamelog_url': self.scraper.base_url.format(season.contents[0]['href'])
                })
        return seasons

    def scrape_player_stats(self):
        """Scrape the stats for all available games for a player"""
        if len(self.seasons_with_stats) > 0:
            for season in self.seasons_with_stats:
                if season['year'] == 'Career' or season['year'] == 'Postseason' or season['year'] == 'Player Game Finder':
                    continue
                self.scrape_season_gamelog(season['gamelog_url'], season['year'])

    def scrape_season_gamelog(self, gamelog_url, year):
        """
        scrape season gamelog for a given year
        """
        soup = self.collect_soup(gamelog_url)
        regular_season_table = soup.find('table', {'id': 'stats'})
        if regular_season_table is None:
            return False
        games = regular_season_table.find('tbody').find_all('tr')

        playoff_table = soup.find('table', {'id': 'stats_playoffs'})
        if playoff_table is not None:
            games += playoff_table.find('tbody').find_all('tr')

        for game in games:
            stats = self.make_player_game_stats(self.player_id, int(year))

            missing_reason = game.find('td', {'data-stat': 'reason'})
            if missing_reason is None:
                stats['game_id'] = str(game.find('td', {'data-stat': 'game_date'}).find('a', href=True)['href'].replace('/boxscores/', '').replace('.htm', ''))
                stats['date'] = str(game.find('td', {'data-stat': 'game_date'}).contents[0].contents[0])
                stats['game_number'] = int(game.find('td', {'data-stat': 'game_num'}).contents[0])
                if game.find('td', {'data-stat': 'age'}) is not None:
                    stats['age'] = float(game.find('td', {'data-stat': 'age'}).contents[0])
                stats['team'] = str(game.find('td', {'data-stat': 'team'}).contents[0].contents[0])
                if game.find('td', {'data-stat': 'game_location'}).contents == ['@']:
                    stats['game_location'] = 'A'
                elif game.find('td', {'data-stat': 'game_location'}).contents == ['N']:
                    stats['game_location'] = 'N'
                else:
                    stats['game_location'] = 'H'
                stats['opponent'] = str(game.find('td', {'data-stat': 'opp'}).contents[0].contents[0])
                result = game.find('td', {'data-stat': 'game_result'}).contents[0].contents[0]
                stats['game_won'] = (result.split(' ')[0] == 'W')
                stats['player_team_score'] = str(result.split(' ')[1].split('-')[0])
                stats['opponent_score'] = str(result.split(' ')[1].split('-')[1])

                # Collect passing stats
                pass_attempts = game.find('td', {'data-stat': 'pass_cmp'})
                if pass_attempts is not None and len(pass_attempts) > 0:
                    stats['passing_attempts'] = int(pass_attempts.contents[0])

                pass_completions = game.find('td', {'data-stat': 'pass_att'})
                if pass_completions is not None and len(pass_completions) > 0:
                    stats['passing_completions'] = int(pass_completions.contents[0])

                pass_yards = game.find('td', {'data-stat': 'pass_yds'})
                if pass_yards is not None and len(pass_yards) > 0:
                    stats['passing_yards'] = int(pass_yards.contents[0])

                pass_touchdowns = game.find('td', {'data-stat': 'pass_td'})
                if pass_touchdowns is not None and len(pass_touchdowns) > 0:
                    stats['passing_touchdowns'] = int(pass_touchdowns.contents[0])

                pass_interceptions = game.find('td', {'data-stat': 'pass_int'})
                if pass_interceptions is not None and len(pass_interceptions) > 0:
                    stats['passing_interceptions'] = int(pass_interceptions.contents[0])

                pass_rating = game.find('td', {'data-stat': 'pass_rating'})
                if pass_rating is not None and len(pass_rating) > 0:
                    stats['passing_rating'] = float(pass_rating.contents[0])

                pass_sacks = game.find('td', {'data-stat': 'pass_sacked'})
                if pass_sacks is not None and len(pass_sacks) > 0:
                    stats['passing_sacks'] = int(pass_sacks.contents[0])

                pass_sacks_yards_lost = game.find('td', {'data-stat': 'pass_sacked_yds'})
                if pass_sacks_yards_lost is not None and len(pass_sacks_yards_lost) > 0:
                    stats['passing_sacks_yards_lost'] = int(pass_sacks_yards_lost.contents[0])

                # Collect rushing stats
                rushing_attempts = game.find('td', {'data-stat': 'rush_att'})
                if rushing_attempts is not None and len(rushing_attempts) > 0:
                    stats['rushing_attempts'] = int(rushing_attempts.contents[0])

                rushing_yards = game.find('td', {'data-stat': 'rush_yds'})
                if rushing_yards is not None and len(rushing_yards) > 0:
                    stats['rushing_yards'] = int(rushing_yards.contents[0])

                rushing_touchdowns = game.find('td', {'data-stat': 'rush_td'})
                if rushing_touchdowns is not None and len(rushing_touchdowns) > 0:
                    stats['rushing_touchdowns'] = int(rushing_touchdowns.contents[0])

                # Collect receiving stats
                receiving_targets = game.find('td', {'data-stat': 'targets'})
                if receiving_targets is not None and len(receiving_targets) > 0:
                    stats['receiving_targets'] = int(receiving_targets.contents[0])

                receiving_receptions = game.find('td', {'data-stat': 'rec'})
                if receiving_receptions is not None and len(receiving_receptions) > 0:
                    stats['receiving_receptions'] = int(receiving_receptions.contents[0])

                receiving_yards = game.find('td', {'data-stat': 'rec_yds'})
                if receiving_yards is not None and len(receiving_yards) > 0:
                    stats['receiving_yards'] = int(receiving_yards.contents[0])

                receiving_touchdowns = game.find('td', {'data-stat': 'rec_td'})
                if receiving_touchdowns is not None and len(receiving_touchdowns) > 0:
                    stats['receiving_touchdowns'] = int(receiving_touchdowns.contents[0])

                # Collect kick return stats
                kick_return_attempts = game.find('td', {'data-stat': 'kick_ret'})
                if kick_return_attempts is not None and len(kick_return_attempts) > 0:
                    stats['kick_return_attempts'] = int(kick_return_attempts.contents[0])

                kick_return_yards = game.find('td', {'data-stat': 'kick_ret_yds'})
                if kick_return_yards is not None and len(kick_return_yards) > 0:
                    stats['kick_return_yards'] = int(kick_return_yards.contents[0])

                kick_return_touchdowns = game.find('td', {'data-stat': 'kick_ret_td'})
                if kick_return_touchdowns is not None and len(kick_return_touchdowns) > 0:
                    stats['kick_return_touchdowns'] = int(kick_return_touchdowns.contents[0])

                # Collect punt return stats
                punt_return_attempts = game.find('td', {'data-stat': 'punt_ret'})
                if punt_return_attempts is not None and len(punt_return_attempts) > 0:
                    stats['punt_return_attempts'] = int(punt_return_attempts.contents[0])

                punt_return_yards = game.find('td', {'data-stat': 'punt_ret_yds'})
                if punt_return_yards is not None and len(punt_return_yards) > 0:
                    stats['punt_return_yards'] = int(punt_return_yards.contents[0])

                punt_return_touchdowns = game.find('td', {'data-stat': 'punt_ret_td'})
                if punt_return_touchdowns is not None and len(punt_return_touchdowns) > 0:
                    stats['punt_return_touchdowns'] = int(punt_return_touchdowns.contents[0])

                # Collect defensive stats
                defense_sacks = game.find('td', {'data-stat': 'sacks'})
                if defense_sacks is not None and len(defense_sacks) > 0:
                    stats['defense_sacks'] = float(defense_sacks.contents[0])

                defense_tackles = game.find('td', {'data-stat': 'tackles_solo'})
                if defense_tackles is not None and len(defense_tackles) > 0:
                    stats['defense_tackles'] = int(defense_tackles.contents[0])

                defense_tackle_assists = game.find('td', {'data-stat': 'tackles_assists'})
                if defense_tackle_assists is not None and len(defense_tackle_assists) > 0:
                    stats['defense_tackle_assists'] = int(defense_tackle_assists.contents[0])

                defense_interceptions = game.find('td', {'data-stat': 'def_int'})
                if defense_interceptions is not None and len(defense_interceptions) > 0:
                    stats['defense_interceptions'] = int(defense_interceptions.contents[0])

                defense_interception_yards = game.find('td', {'data-stat': 'def_int_yds'})
                if defense_interception_yards is not None and len(defense_interception_yards) > 0:
                    stats['defense_interception_yards'] = int(defense_interception_yards.contents[0])

                defense_safeties = game.find('td', {'data-stat': 'safety_md'})
                if defense_safeties is not None and len(defense_safeties) > 0:
                    stats['defense_safeties'] = int(defense_safeties.contents[0])

                # Collect kicking stats
                point_after_attemps = game.find('td', {'data-stat': 'xpm'})
                if point_after_attemps is not None and len(point_after_attemps) > 0:
                    stats['point_after_attemps'] = int(point_after_attemps.contents[0])

                point_after_makes = game.find('td', {'data-stat': 'xpa'})
                if point_after_makes is not None and len(point_after_makes) > 0:
                    stats['point_after_makes'] = int(point_after_makes.contents[0])

                field_goal_attempts = game.find('td', {'data-stat': 'fga'})
                if field_goal_attempts is not None and len(field_goal_attempts) > 0:
                    stats['field_goal_attempts'] = int(field_goal_attempts.contents[0])

                field_goal_makes = game.find('td', {'data-stat': 'fgm'})
                if field_goal_makes is not None and len(field_goal_makes) > 0:
                    stats['field_goal_makes'] = int(field_goal_makes.contents[0])

                # Collect punting stats
                punting_attempts = game.find('td', {'data-stat': 'punt'})
                if punting_attempts is not None and len(punting_attempts) > 0:
                    stats['punting_attempts'] = int(punting_attempts.contents[0])

                punting_yards = game.find('td', {'data-stat': 'punt_yds'})
                if punting_yards is not None and len(punting_yards) > 0:
                    stats['punting_yards'] = int(punting_yards.contents[0])

                punting_blocked = game.find('td', {'data-stat': 'punt_blocked'})
                if punting_blocked is not None and len(punting_blocked) > 0:
                    stats['punting_blocked'] = int(punting_blocked.contents[0])

                self.game_stats.append(stats)

    def consolidate(self):
        self.profile['is_historic'] = self.game_stats[-1]['year'] != str(2021)
        self.profile['rookie_year'] = int(self.game_stats[0]['year'])
        final_game_year = int(self.game_stats[-1]['year'])
        self.profile['experience'] = final_game_year - self.profile['rookie_year']
        self.profile['status'] = 'retired' if self.profile['is_historic'] else 'active'