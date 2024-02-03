import pymysql


class MySQLDatabase:
    def __init__(self, host, user, password, db):
        self.connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=db,
            charset='gbk',
            cursorclass=pymysql.cursors.DictCursor
        )

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def sign_in(self, account, password):
        with self.connection.cursor() as cursor:
            sql = "CALL sign_in(%s, %s)"
            cursor.execute(sql, (account, password))
            result = cursor.fetchone()
            return result['result'] == 1

    def register(self, account_name, password, email):
        with self.connection.cursor() as cursor:
            sql = """
            INSERT INTO users (account_name, password, email) 
            VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (account_name, password, email))
        self.connection.commit()

    def add_dialog(self, user_id, message, is_user):
        with self.connection.cursor() as cursor:
            sql = """
            INSERT INTO dialogs (user_id, message, is_user) 
            VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (user_id, message, is_user))
        self.connection.commit()

    def delete_dialog(self, dialog_id):
        with self.connection.cursor() as cursor:
            sql = "DELETE FROM dialogs WHERE dialog_id = %s"
            cursor.execute(sql, (dialog_id,))
        self.connection.commit()

    def get_dialog(self, dialog_id, user_id, is_user):
        with self.connection.cursor() as cursor:
            sql = """
            SELECT * FROM dialogs 
            WHERE dialog_id = %s AND user_id = %s AND is_user = %s
            """
            cursor.execute(sql, (dialog_id, user_id, is_user))
            return cursor.fetchall()

    def get_latest_image(self, dialog_id):
        with self.connection.cursor() as cursor:
            sql = """
            SELECT * FROM images 
            WHERE dialog_id = %s 
            ORDER BY time DESC 
            LIMIT 1
            """
            cursor.execute(sql, (dialog_id,))
            return cursor.fetchone()
