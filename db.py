import psycopg2
from urllib.parse import urlparse
from uuid import uuid4

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

    def get_user_mode(self, uid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             select umode, pollid from user_mode where uid='{}';
                             '''.format(uid))
                mode_data = curs.fetchall()
                data_row = mode_data[0] if mode_data else None
                umode = data_row[0] if data_row else 'Ready'
                pollid = data_row[1] if data_row else None
        return umode, pollid

    def set_user_mode(self, uid, umode, pollid=None):
        # Modes: 'Ready', 'Question', 'Answer'
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             insert into user_mode (uid, umode, pollid) 
                             values ('{0}', '{1}', '{2}')
                             on conflict (uid) do update set umode='{1}', pollid='{2}';
                             '''.format(uid, umode, (pollid or 'NULL')))

    def create_poll(self, question, author):
        pid = str(uuid4())
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             insert into poll (pollid, question, author, isactive) 
                             values ('{0}', '{1}', {2}, {3});
                             '''.format(pid, question, author, False))
        return pid
    
    def set_poll_active(self, pid, isactive=True):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             update poll set isactive={0} where pollid='{1}';
                             '''.format(isactive, pid))

    def is_poll_active(self, pid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             select isactive from poll where pollid='{0}';
                             '''.format(pid))
                result = curs.fetchall()
                isactive = result[0][0] if result and result[0] else False
        return isactive

    def poll_exists(self, pid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             select pollid from poll where pollid='{0}';
                             '''.format(pid))
                result = curs.fetchall()
                exists = result and result[0] and result[0][0]
        return exists

    def delete_poll(self, pid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             delete from poll where pollid='{}';
                             '''.format(pid))

    def add_answer(self, pid, answer):
        answerid = str(uuid4())
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             insert into answer (answerid, pollid, answer) 
                             values ('{0}', '{1}', '{2}');
                             '''.format(answerid, pid, answer))
        return answerid
    
    def add_user_answer(self, uid, pid, answerid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             insert into answer (uid, pollid, answerid) 
                             values ('{0}', '{1}', '{2}');
                             '''.format(uid, pid, answerid))

    def get_user_poll_list(self, uid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             select question from poll where author={0};
                             '''.format(uid))
                polls = curs.fetchall()
        return polls

    def get_answer_list(self, pid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             select answer from answer where pollid='{0}';
                             '''.format(pid))
                answers = curs.fetchall()
        return answers

    def get_answer_count_list(self, pid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             select answer, max(count (answer) over (partition by answer))
                             from answer 
                             where pollid='{0}'
                             group by answer;
                             '''.format(pid))
                answers = curs.fetchall()
        return answers
    
    def get_user_answer(self, pid, uid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             select answer from answer a
                             inner join user_answer ua 
                             on a.answerid=ua.answerid
                             where ua.uid='{0}' and ua.pollid='{1}';
                             '''.format(uid, pid))
                answers = curs.fetchall()
        return answers

