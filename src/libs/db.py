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
            print(result)
            if (result['result'] == 0):
                return 0
            else:
                return result['result']

    def register(self, account, password, email):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO users (account_name, password, email) VALUES (%s, %s, %s)"
            cursor.execute(sql, (account, password, email))
        self.connection.commit()

    def deregister(self, account):
        with self.connection.cursor() as cursor:
            sql = "DELETE FROM users WHERE account_name = %s"
            cursor.execute(sql, (account,))
        self.connection.commit()

    def get_dialogs(self, user_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM dialogs WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchall()
            return result

    def get_texts(self, dialog_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM texts WHERE dialog_id = %s"
            cursor.execute(sql, (dialog_id,))
            result = cursor.fetchall()
            return result

    def get_image_by_text_id(self, text_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM images WHERE text_id = %s"
            cursor.execute(sql, (text_id,))
            result = cursor.fetchone()
            return result

    def get_latest_image(self, dialog_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM images WHERE dialog_id = %s ORDER BY time DESC LIMIT 1"
            cursor.execute(sql, (dialog_id,))
            result = cursor.fetchone()
            return result

    def delete_dialog(self, dialog_id):
        with self.connection.cursor() as cursor:
            sql = "DELETE FROM dialogs WHERE dialog_id = %s"
            cursor.execute(sql, (dialog_id,))
        self.connection.commit()

    def add_dialog(self, user_id, name):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO dialogs (user_id, name) VALUES (%s, %s)"
            cursor.execute(sql, (user_id, name))
        self.connection.commit()

    def delete_text(self, text_id):
        with self.connection.cursor() as cursor:
            sql = "DELETE FROM texts WHERE text_id = %s"
            cursor.execute(sql, (text_id,))
        self.connection.commit()

    def add_text(self, dialog_id, from_, has_img, message):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO texts (dialog_id, from, has_img, message) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (dialog_id, from_, has_img, message))
        self.connection.commit()

    def delete_image(self, text_id):
        with self.connection.cursor() as cursor:
            sql = "DELETE FROM images WHERE text_id = %s"
            cursor.execute(sql, (text_id,))
        self.connection.commit()

    def add_image(self, dialog_id, text_id, image):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO images (dialog_id, text_id, image) VALUES (%s, %s, %s)"
            cursor.execute(sql, (dialog_id, text_id, image))
        self.connection.commit()

    def close(self):
        self.connection.close()
