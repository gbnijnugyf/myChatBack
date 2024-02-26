import base64
import binascii

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
            sql = "UPDATE users SET is_del = 1 WHERE account_name = %s"
            cursor.execute(sql, (account,))
        self.connection.commit()

    def get_dialogs(self, user_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM dialogs WHERE user_id = %s AND is_del = 0"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchall()
            return result

    def get_dialog(self, session_name):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM dialogs WHERE name = %s AND is_del = 0"
            cursor.execute(sql, (session_name,))
            result = cursor.fetchone()
            return result

    def get_texts(self, dialog_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM texts WHERE dialog_id = %s AND is_del = 0"
            cursor.execute(sql, (dialog_id,))
            result = cursor.fetchall()
            return result

    def get_image_by_text_id(self, text_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM images WHERE text_id = %s AND is_del = 0"
            cursor.execute(sql, (text_id,))
            result = cursor.fetchone()
            return result

    def get_latest_image(self, dialog_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM images WHERE dialog_id = %s AND is_del = 0 ORDER BY time DESC LIMIT 1"
            cursor.execute(sql, (dialog_id,))
            return cursor.fetchone()['image']

    def delete_dialog(self, dialog_id):
        try:
            with self.connection.cursor() as cursor:
                sql = "UPDATE dialogs SET is_del = 1 WHERE dialog_id = %s"
                cursor.execute(sql, (dialog_id,))
            self.connection.commit()
            return True  # 返回True表示删除成功
        except Exception as e:
            print(f"Error: {e}")
            self.connection.rollback()
            return False  # 返回False表示删除失败

    def add_dialog(self, user_id, name):
        try:
            with self.connection.cursor() as cursor:
                try:
                    cursor.execute("START TRANSACTION")
                    sql = "INSERT INTO dialogs (user_id, name) VALUES (%s, %s)"
                    cursor.execute(sql, (user_id, name))
                    cursor.execute("COMMIT")
                except Exception as e:
                    cursor.execute("ROLLBACK")
                    raise
                try:
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    dialog_id = cursor.fetchone()['LAST_INSERT_ID()']
                    return dialog_id
                except Exception as e:
                    print(f"Error: {e}")
                    return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    def delete_text(self, text_id):
        try:
            with self.connection.cursor() as cursor:
                sql = "UPDATE texts SET is_del = 1 WHERE text_id = %s"
                cursor.execute(sql, (text_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def add_text(self, dialog_id, from_, has_img, message):
        try:
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO texts (dialog_id, is_ai, has_img, message) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (dialog_id, from_, has_img, message))
                cursor.execute("SELECT LAST_INSERT_ID()")
                text_id = cursor.fetchone()['LAST_INSERT_ID()']  # 获取刚插入的文本的ID
            self.connection.commit()
            return text_id
        except Exception as e:
            print(f"Error: {e}")
            return False

    def delete_image(self, text_id):
        with self.connection.cursor() as cursor:
            sql = "update images set is_del = 1 where text_id = %s"
            cursor.execute(sql, (text_id,))
        self.connection.commit()

    def add_image(self, dialog_id, text_id, image):
        try:
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO images (dialog_id, text_id, image) VALUES (%s, %s, %s)"
                cursor.execute(sql, (dialog_id, text_id, image))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def get_image(self, text_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT image FROM images WHERE text_id = %s AND is_del = 0"
            cursor.execute(sql, (text_id,))
            return cursor.fetchone()['image']

    def get_latest_messages_and_image(self, text_id):
        try:
            with self.connection.cursor() as cursor:
                # 查询text_id对应的dialog_id
                sql = "SELECT dialog_id FROM texts WHERE text_id = %s AND is_del = 0"
                cursor.execute(sql, (text_id,))
                dialog_id = cursor.fetchone()['dialog_id']
                if dialog_id is None:
                    print(f"No dialog found for text_id {text_id}")
                    return None

                # 查询最新的20条记录
                sql = """
                SELECT * FROM texts 
                WHERE dialog_id = %s AND is_del = 0 
                ORDER BY time DESC 
                LIMIT 20
                """
                cursor.execute(sql, (dialog_id,))
                messages = cursor.fetchall()

                # 查询最新的一张图片
                sql = """
                SELECT * FROM images 
                WHERE dialog_id = %s AND is_del = 0 
                ORDER BY time DESC 
                LIMIT 1
                """
                cursor.execute(sql, (dialog_id,))
                image = cursor.fetchone()
                if image is not None:
                    image = image['image']
            self.connection.commit()
            return messages, image
        except Exception as e:
            print(f"Error: {e}")
            return None

    def close(self):
        self.connection.close()

    # def get_image_as_base64(self, text_id):
    #     try:
    #         with self.connection.cursor() as cursor:
    #             sql = "SELECT image FROM images WHERE text_id = %s"
    #             cursor.execute(sql, (text_id,))
    #             result = cursor.fetchone()
    #             if result is not None:
    #                 image_data = result['image']
    #                 # 将图片数据转换为Base64编码的字符串
    #                 image_base64 = base64.b64encode(image_data).decode()
    #                 return image_base64
    #             else:
    #                 print("No image found with the provided text_id.")
    #                 return None
    #     except Exception as e:
    #         print(f"Error: {e}")
    #         return None

    # def get_image(self, dialog_id, text_id):
    #     try:
    #         with self.connection.cursor() as cursor:
    #             sql = "SELECT image FROM images WHERE dialog_id = %s AND text_id = %s"
    #             cursor.execute(sql, (dialog_id, text_id))
    #             result = cursor.fetchone()
    #             if result is not None:
    #                 image_data = result[0]
    #                 return image_data
    #             else:
    #                 print("No image found with the provided dialog_id and text_id.")
    #                 return None
    #     except Exception as e:
    #         print(f"Error: {e}")
    #         return None
