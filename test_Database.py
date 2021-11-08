from unittest import TestCase
from Database import Database
import datetime as dt

class TestDatabase(TestCase):
    def test_insert_player(self):
        self.fail()


    def test_connect(self):
        host = "encorefan.com"
        db_name = "test"
        user = "saruben"
        password = "Win$ton128"
        db = Database(host=host, db_name=db_name, user=user, password=password)
        self.assertIsNotNone(db.cursor)


    def test_query(self):
        db = Database(user="root", password="Ruben-5AW", db_name='encorefan')
        get_id_statement = ("SELECT MAX(id) from `players`")
        db.cursor.execute(get_id_statement)
        var = db.cursor[0]
        db.close()

    def test_player_table_insert(self):
        p = {
            'id': 1,
            'team_id': 1,
            'first_name': 'Anna',
            'last_name': 'Pignone',
            'position_id': 1,
            'pro_league_id': 1,
            'pro_team_id': 1,
            'status': 2,
            'birthday': '12-05-2021',
            'weight': 120,
            'height': 61,
            'birth_city': 'Lemont',
            'birth_state': 'IL',
            'college': 'Michigan State University',
            'college_conf': 'Big 10',
            'rookie_year': 2021,
            'draft_year': 2021,
            'draft_round': 1,
            'draft_position': 1,
            'draft_team_id': 22,
            'salary': 1000000,
            'img_uri': 'link',
            'experience': 1.2,
            'hof_induction': 2017,
            'is_historic': 0
        }

        db = Database(user="root", password="Ruben-5AW", db_name='encorefan')
        insert_statement = (
            "INSERT INTO `players` "
            "values({id}, "
            "'{first_name}', '{last_name}', {position_id}, {pro_league_id}, {pro_team_id}, {status}, '{birthday}',"
            "{weight}, {height}, '{birth_city}', '{birth_state}', '{college}', '{college_conf}',"
            "{rookie_year}, {draft_year}, {draft_round}, {draft_position}, {draft_team_id}, {salary}, '{img_uri}',"
            " {experience}, {hof_induction}, {is_historic},"
            "{created_at}, {updated_at})").format(
            id=2, first_name=p['first_name'], last_name=p['last_name'],
            position_id=p['position_id'], pro_league_id=p['pro_league_id'], pro_team_id=p['pro_team_id'], status=p['status'],
            birthday=dt.datetime.now(), weight=p['weight'], height=p['height'], birth_city=p['birth_city'], birth_state=p['birth_state'],
            college=p['college'], college_conf=p['college_conf'], rookie_year=p['rookie_year'], draft_year=p['draft_year'],
            draft_round=p['draft_round'], draft_position=p['draft_position'], draft_team_id=p['draft_team_id'],
            salary=p['salary'], img_uri=p['img_uri'], experience=p['experience'], hof_induction=p['hof_induction'],
            is_historic=p['is_historic'], created_at='10/21/2021', updated_at='10/21/2021')

        db.save_player_profile(p)


