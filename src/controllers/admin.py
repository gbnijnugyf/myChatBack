from flask import Blueprint, jsonify, make_response, request
from models.DTO import ReturnDTO
from application import cipher_suite, app
from libs.db import mysql
from datetime import datetime, timedelta

admin = Blueprint("admin", __name__)


@admin.route("/login", methods=["POST"])
def login():
    """管理员登录"""
    try:
        username = str(request.json.get("userName"))
        password = str(request.json.get("passWord"))
        if "-" in username or "-" in password:
            raise Exception("账号或密码中不得出现特殊字符")

        # 进行数据库验证
        dbObj = mysql()
        ret = dbObj.checkPassword(username, password)
        dbObj.close()
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

        # response.set_cookie(
        #     app.config["AUTH_COOKIE_NAME"], cipher_text.decode("utf-8"), max_age=60 * 60
        # )
        print(cipher_text.decode("utf-8"))

        return response
    except Exception as e:
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0})
        return jsonify(returnDTO.to_dict())


@admin.route("/logout")
def logout():
    """管理员登出"""
    try:
        returnDTO = ReturnDTO.from_dict({"msg": "success", "status": 1})
        response = make_response(jsonify(returnDTO.to_dict()))
        response.delete_cookie(app.config["AUTH_COOKIE_NAME"])
        return response
    except Exception as e:
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0})
        return jsonify(returnDTO.to_dict())


@admin.route("/edit", methods=["POST"])
def adminInfoEdit():
    pass
