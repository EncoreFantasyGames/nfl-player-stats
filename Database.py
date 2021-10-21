import mysql.connector as sql


class Database:
    def __init__(self, db_name, user, password, host='127.0.0.1', port='3306'):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.user = user
        self.password = password

        # connect
        try:
            self.cnx = sql.connect(user=user, password=password,
                                      host=host, database=db_name)
            self.cursor = self.cnx.cursor()
        except Exception as err:
            print("ERROR: {}".format(err))
            raise

    def close(self):
        self.cnx.close()

    def insert_player(self, profile):
        self.cursor.execute()

    def insert_game(self, game, player_id, player_name):
        pass

