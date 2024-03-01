from flask import Flask
from flask_cors import CORS
import logging
import click
from cryptography.fernet import Fernet

from libs.db import MySQLDatabase
# from flask import Blueprint, request, jsonify, make_response
# from datetime import datetime, timedelta
# from models.DTO import ReturnDTO


app = Flask(__name__, static_folder="../static", static_url_path="/static")
CORS(app)
app.config.from_pyfile("config/settings.py")

# handler = logging.FileHandler("../root/autodl-tmp/myChat/myChat/logs/app.log", encoding="UTF-8")
handler = logging.FileHandler("/root/autodl-tmp/myChat/myChat/logs/app.log", encoding="UTF-8")
handler.setLevel(
    logging.DEBUG
)  # 设置日志记录最低级别为DEBUG，低于DEBUG级别的日志记录会被忽略，不设置setLevel()则默认为NOTSET级别。
logging_format = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s"
)
handler.setFormatter(logging_format)
app.logger.addHandler(handler)

# hostname = "http://" + str(socket.gethostbyname(socket.gethostname())) + ":5000"
# hostname = "http://localhost:6006"
key = Fernet.generate_key()  # 生成一个Fernet加密密钥。
cipher_suite = Fernet(key)  # 使用密钥创建一个Fernet加密套件。

# 初始化你的数据库类
# db = MySQLDatabase(host='127.0.0.1', user='root', password='123456', db='my_chat')
db = MySQLDatabase(host='127.0.0.1', user='root', password='123456', db='my_chat')


# import sys
# sys.path.append('/root/autodl-tmp/LLaVA/')
# from MultiRoundModel import MultiRoundModel
# model = MultiRoundModel()

# ### Test Model
# inputText = [[0,"What's your name"],
#              [1,"My name is LLaVA"],
#              [0,"Where is Beijing and what is in the picture?"]]

# outputs = model.arrayConversation(inputText,"/root/autodl-tmp/LLaVA/R.jpg")
# print("Model :",outputs)

# print("\n\n     Model is OK! \n\n")
# ### end Test Model


# 运行前模型测试 begin
# message, image = db.get_latest_messages_and_image(3)
# print(message, image)
# # 转为二维list
# msgList = [[item['is_ai'], item['message']] for item in message]
# print(msgList, image)
# # 模型处理......
# print(model.arrayConversation(msgList,image))
# 运行前模型测试 end

@app.cli.command()
def initdb():
    # db.create_all()
    click.echo("Initialized database.")


@app.cli.command()
def runserver():
    app.run(debug=True)


def main():
    app.run(host="127.0.0.1", port=6006,debug=True)

if __name__ == "__main__":
    # save_image_to_file()
    # model = MultiRoundModel()
    try:
        import sys
        from www import *
        sys.exit(main())
    except Exception as e:
        import traceback

        traceback.print_exc()


# @app.route('/users/login', methods=["POST"])
# def login():
#     """管理员登录"""
#     try:
#         username = str(request.json.get("name"))
#         password = str(request.json.get("password"))
#         print(username, password)
#         if "-" in username or "-" in password:
#             raise Exception("账号或密码中不得出现特殊字符")
#
#         # 进行数据库验证
#         ret = db.sign_in(username, password)
#
#         if ret == 0:  # 验证登录状态
#             raise Exception("账号或密码错误")
#
#         nextTime = datetime.now() + timedelta(seconds=120)
#         message = "{}-{}-{}".format(
#             username, password, nextTime.strftime("%Y#%m#%d#%H:%M:%S")
#         ).encode("utf-8")
#         cipher_text = cipher_suite.encrypt(message)
#
#         returnDTO = ReturnDTO.from_dict({"msg": "success", "status": 1}).to_dict()
#         returnDTO["data"] = cipher_text.decode("utf-8")
#         response = make_response(jsonify(returnDTO))
#         # response.headers['Access-Control-Expose-Headers'] = "*"
#         print(cipher_text.decode("utf-8"))
#
#         return response
#     except Exception as e:
#         returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0}).to_dict()
#         return jsonify(returnDTO)
