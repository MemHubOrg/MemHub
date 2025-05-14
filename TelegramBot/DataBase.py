import psycopg2
from psycopg2 import sql


class DB():
    def __init__(self, db_name: str, db_user: str, db_password: str, db_host: str, db_port: int):
        self.database = db_name
        self.user = db_user
        self.password = db_password
        self.host = db_host
        self.port = db_port
        self.conn = None
        self.cur = None

        self.connect()

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                database=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cur = self.conn.cursor()
        except Exception as e:
            print(f"Could not connect to the database: {e}")
            raise

    def update_data(self, data: str, username: str):
        try:
            self.cur.execute(
                sql.SQL(
                    """
                    update django_db.public.register_user 
                    set chat_id = %s
                    where username = %s
                    """
                ), (data, username)
            )
            self.conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_data(self, data_type: str, username: str) -> str:
        data = self.get_db_data(username)
        if not data:
            return "No data found."

        if data_type == "username":
            return data[0][3]
        elif data_type == "chat_id":
            return data[0][5]
        elif data_type == "secret":
            return data[0][4]
        else:
            return "Invalid data type."

    def get_db_data(self, identifier: str):
        try:
            self.cur.execute(
                sql.SQL("""
                    SELECT * FROM django_db.public.register_user WHERE chat_id = %s or username = %s
                """),
                (identifier, identifier)
            )
            return self.cur.fetchall()
        except Exception as e:
            print(f"An error occurred: {e}")

    def create_user_with_chat_id(self, username: str, chat_id: str):
        try:
            self.cur.execute(
                sql.SQL("""
                    INSERT INTO django_db.public.register_user (username, chat_id, unique_token, password, is_active, force_password_reset)
                    VALUES (%s, %s, NULL, '', True, False)
                    ON CONFLICT (username) DO NOTHING
                """),
                (username, chat_id)
            )
            self.conn.commit()
            print(f"[INFO] Created new user in DB: username={username}, chat_id={chat_id}")
        except Exception as e:
            print(f"[ERROR] create_user_with_chat_id: {e}")