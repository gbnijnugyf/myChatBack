from flask import Blueprint, request, jsonify, make_response
from datetime import datetime, timedelta
from src.application import db, cipher_suite
from src.models.DTO import ReturnDTO

user = Blueprint("user", __name__)


@user.route("/login", methods=["POST"])
def login():
    """管理员登录"""
    try:
        username = str(request.json.get("name"))
        password = str(request.json.get("password"))
        print(username, password)
        if "-" in username or "-" in password:
            raise Exception("账号或密码中不得出现特殊字符")

        # 进行数据库验证
        ret = db.sign_in(username, password)

        if ret == 0:  # 验证登录状态
            raise Exception("账号或密码错误")

        nextTime = datetime.now() + timedelta(seconds=120)
        message = "{}-{}-{}".format(
            username, password, nextTime.strftime("%Y#%m#%d#%H:%M:%S")
        ).encode("utf-8")
        cipher_text = cipher_suite.encrypt(message)

        returnDTO = ReturnDTO.from_dict({"msg": "success", "status": 1}).to_dict()
        returnDTO["data"] = cipher_text.decode("utf-8")
        response = make_response(jsonify(returnDTO))
        # response.headers['Access-Control-Expose-Headers'] = "*"
        print(cipher_text.decode("utf-8"))

        return response
    except Exception as e:
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0}).to_dict()
        return jsonify(returnDTO)
