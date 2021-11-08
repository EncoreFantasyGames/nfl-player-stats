import mysql.connector as sql
import datetime as dt

class Database:
    def __init__(self, db_name, user, password, host='127.0.0.1', port='3306'):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.user = user
        self.password = password

        self.cnx = None
        self.cursor = None
        self.connect()

    def connect(self):
        # connect
        print("Attempting Connection")
        try:
            self.cnx = sql.connect(user=self.user, password=self.password,
                                   host=self.host, database=self.db_name)
            self.cursor = self.cnx.cursor()
            print("Connected!")
        except Exception as err:
            print("ERROR: {}".format(err))
            raise

    def close(self):
        self.cursor.close()
        self.cnx.close()
        print("DB Connection Closed")

    def record_exists(self, table, _id):
        query = None
        if table == 'player':
            query = "SELECT id as 'id' FROM `players` WHERE first_name=%s and last_name=%s and position_id=%s"

        self.cursor.execute(query, _id)
        var = self.cursor.fetchone()  # gets first row from response and moves to the 'next' until no more rows
        return var is not None

    def lookup_position_id(self, _handle):
        try:
            query = (" SELECT id FROM position WHERE handle='{0}' LIMIT 1".format(str(_handle)))
            self.cursor.execute(query)
            var = self.cursor.fetchone()
            return var[0]  # gets id from tuple of row
        except Exception as err:
            raise Exception(err)

    def lookup_team_id(self, _handle):
        now = dt.datetime.now().date()
        query = None
        if _handle is None:
            return None

        if len(_handle.split(" ")) > 1:
            team_name = str(_handle.split(" ")[-1])
            # handle case of "football team"
            if _handle.split(" ")[0] == "Washington":
                team_name = "Football Team"
            query = "SELECT id FROM `pro_team` WHERE name='{0}'".format(team_name)
        else:
            query = (" SELECT id FROM `pro_team` WHERE handle='{0}' LIMIT 1".format(str(_handle)))

        try:
            self.cursor.execute(query)
            var = self.cursor.fetchone()
            if var is None:  # no team exists need to insert record and use new id
                get_max_id = "SELECT max(id) FROM `pro_team` ORDER BY 1 DESC"
                self.cursor.execute(get_max_id)
                new_id = self.cursor.fetchone()[0] + 1  # get max id

                insert_new_team = "INSERT INTO `pro_team` VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                vars = (new_id, 'NAME', 'LOCALE', _handle, None, 0, None, None, str(now), str(now))
                self.cursor.execute(insert_new_team, vars)
                self.cnx.commit()
                return new_id

            return var[0]  # gets id from tuple of row
        except Exception as err:
            raise Exception(err)
    
    def save_player_profile(self, p):
        now = dt.datetime.now().date()
        position_id = self.lookup_position_id(p['position'])
        team_id = self.lookup_team_id(p['current_team'])
        draft_team_id = self.lookup_team_id(p['draft_team'])

        if not self.record_exists('player', (p['first_name'], p['last_name'], position_id)):
            statement = """ INSERT INTO `players` 
                        (first_name, last_name, position_id, pro_league_id, pro_team_id, 
                         status_id, dob, weight, height, birth_city, 
                         birth_state, college, college_conf, rookie_year, draft_year, 
                         draft_round, draft_position, draft_team_id, salary, headshot_uri, 
                         experience, hof_induction_year, is_historical, created_at, updated_at)
                         VALUES (
                         %s, %s, %s, %s, %s, 
                         %s, %s, %s, %s, %s,
                         %s, %s, %s, %s, %s,
                         %s, %s, %s, %s, %s, 
                         %s, %s, %s, %s, %s) """

            vars = ( p['first_name'], p['last_name'], position_id, 1, team_id,
                     0, p['birth_date'], p['weight'], p['height'], p['birth_city'],
                     p['birth_state'], p['college'], None, p['rookie_year'], p['draft_year'],
                     p['draft_round'], p['draft_position'], draft_team_id, p['current_salary'], None,
                     p['experience'], p['hof_induction_year'], p['is_historic'], str(now), str(now))

            self.cursor.execute(statement, vars)
            self.cnx.commit()

            find_player_id = """ SELECT id FROM `players` WHERE first_name=%s and last_name=%s and position_id=%s"""
            params = (p['first_name'], p['last_name'], position_id)
            self.cursor.execute(find_player_id, params)
            result = self.cursor.fetchone()
            return result[0]


    def insert_game(self, games, player_id):
        for g in games:
            now = dt.datetime.now().date()
            team_id = self.lookup_team_id(g['team'])
            opponent_id = self.lookup_team_id(g['opponent'])

            statement = """ INSERT INTO `nfl_game_stats`
                        (player_id, year, game_id, date, game_number, 
                        age, team_id, game_location, opponent_team_id, is_game_won, 
                        team_score, opponent_team_score, passing_attempts, passing_completions, passing_yards, 
                        passing_rating, passing_touchdowns, passing_interceptions, passing_sacks, passing_sacks_yards_lost,
                        rushing_attempts, rushing_yards, rushing_touchdowns, receiving_targets, receiving_receptions,
                        receiving_yards, receiving_touchdowns, kick_return_attempts, kick_return_yards, kick_return_touchdowns, 
                        punt_return_attempts, punt_return_yards, punt_return_touchdowns, defense_sacks, defense_tackles, 
                        defense_tackle_assists, defense_interceptions, defense_interception_yards, defense_interception_touchdowns, defense_safeties, 
                        point_after_attempts, point_after_makes, field_goal_attempts, field_goal_makes, punting_attempts, 
                        punting_yards, punting_blocked, created_at, updated_at)
                        VALUES (
                        %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s) """

            vars = (player_id, g['year'], g['game_id'], g['date'], g['game_number'],
                     g['age'], team_id, g['game_location'], opponent_id, g['game_won'],
                     g['player_team_score'], g['opponent_score'], g['passing_attempts'], g['passing_completions'], g['passing_yards'],
                     g['passing_rating'], g['passing_touchdowns'], g['passing_interceptions'], g['passing_sacks'], g['passing_sacks_yards_lost'],
                     g['rushing_attempts'], g['rushing_yards'], g['rushing_touchdowns'], g['receiving_targets'], g['receiving_receptions'],
                     g['receiving_yards'], g['receiving_touchdowns'], g['kick_return_attempts'], g['kick_return_yards'], g['kick_return_touchdowns'],
                     g['punt_return_attempts'], g['punt_return_yards'], g['punt_return_touchdowns'], g['defense_sacks'], g['defense_tackles'],
                     g['defense_tackle_assists'], g['defense_interceptions'], g['defense_interception_yards'], g['defense_interception_touchdowns'], g['defense_safeties'],
                     g['point_after_attempts'], g['point_after_makes'], g['field_goal_attempts'], g['field_goal_makes'], g['punting_attempts'],
                     g['punting_yards'], g['punting_blocked'], str(now), str(now))

            self.cursor.execute(statement, vars)
            self.cnx.commit()

