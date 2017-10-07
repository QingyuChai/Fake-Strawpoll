import rethinkdb as r


class Database:

    def __init__(self):
        self.c = self.get_connection()

    def get_connection(self) -> r.net.DefaultConnection:
        if self.is_first_run():
            print("Setting up Database...")
            return self.setup()
        else:
            return r.connect(db='Strawpoll')

    @staticmethod
    def get_time(self=None) -> str:
        """
        Get current time in string format
        """
        now = datetime.utcnow()
        # Only uncomment the below when on DO server!
        # now = now + timedelta(hours=2)
        time = '{:%d/%m/%Y %H:%M:%S}'.format(now)
        return time

    def is_first_run(self) -> bool:
        """
        If this class is run for the first time EVER, this function returns
        True, and checks by looking for the DB name in the RethinkDB Database
        list.
        """
        return False if "Strawpoll" in r.db_list().run(r.connect()) else True

    def setup(self) -> r.net.DefaultConnection:
        """
        If is_first_run() returns True, then this code will run. This sets up
        the Database.
        """
        setup_c = r.connect()
        r.db_create("Strawpoll").run(setup_c)
        setup_c.use("Strawpoll")
        r.table_create("Options").run(setup_c)
        return setup_c

    def already_exists(self, option) -> bool:
        if r.table("Options").filter(
                {'option': option}).count().run(self.c) == 0:
            return False
        else:
            return True

    def create_option(self, option):
        simple_dict = {
            'option': option,
            'votes': 0
        }
        r.table("Options").insert(simple_dict).run(self.c)

    def add_vote(self, option):
        query_result = r.table("Options").filter(
            {'option': option}
        ).distinct().run(self.c)

        votes = query_result[0]['votes']
        votes += 1

        r.table("Options").filter(
            {'option': option}).update({"votes": votes}).run(self.c)

    def get_votes(self, option) -> int:
        query_result = r.table("Options").filter(
            {'option': option}
        ).distinct().run(self.c)

        votes = query_result[0]['votes']
        return votes

    def get_options(self) -> dict:
        options = {}
        for option in r.table("Options").run(self.c):
            name = option['option']
            votes = option['votes']
            options[name] = votes
        return options
