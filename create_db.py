import psycopg2
from urllib.parse import urlparse

class DB:

    def __init__(self):
        #db_config = urlparse(os.environ['DATABASE_URL'])
        db_url = ''
        db_config = urlparse(db_url)
        self.conn=psycopg2.connect(user=db_config.username,
                                     password=db_config.password,
                                     database=db_config.path[1:],
                                     host=db_config.hostname)

    def __del__(self):
        self.conn.close()

    def create_user_mode_tbl(self):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                    create table user_mode (
                    uid bigint primary key,
                    umode varchar(8)
                    );
                ''')

    def create_poll_tbl(self):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                    create table poll (
                    pollid varchar(40) primary key,
                    question text,
                    isactive boolean
                    );
                ''')

    def create_answer_tbl(self):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                    create table answer (
                    answerid varchar(40) primary key,
                    pollid varchar(40) references poll on delete cascade,
                    answer text
                    );
                ''')

    def create_user_answer_tbl(self):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                    create table user_answer (
                    uid bigint,
                    pollid varchar(40) references poll on delete cascade,
                    answerid varchar(40) references answer on delete cascade,
                    primary key (uid, answerid)
                    );
                ''')

    def create_tbls(self):
        self.create_user_mode_tbl()
        self.create_poll_tbl()
        self.create_answer_tbl()
        self.create_user_answer_tbl()

if __name__ == '__main__':
    db = DB()
    db.create_tbls()
