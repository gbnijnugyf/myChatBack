from flask import request, jsonify
from datetime import datetime

from application import app, cipher_suite, db
from models.DTO import ReturnDTO
from functools import wraps


def cookie_check(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            sign = request.cookies.get(app.config["AUTH_COOKIE_NAME"])
            if sign is None:
                raise Exception("未检查到登录信息")

            # 解密sign
            try:
                plain_text = cipher_suite.decrypt(sign.encode("utf-8")).decode("utf-8")
            except Exception as e:
                raise Exception("密文匹配失败")

            username = plain_text.split("-")[0]
            password = plain_text.split("-")[1]
            nextTime = plain_text.split("-")[2]
            nextTime = datetime.strptime(nextTime, "%Y#%m#%d#%H:%M:%S")
            if nextTime < datetime.now():
                raise Exception("登录信息失效")

            # 进行数据库验证
            ret = db.sign_in(username, password)
            if ret == 0:  # 验证登录状态
                raise Exception("账号或密码错误")

            kwargs = {"user_id": ret}
            return func(*args, **kwargs)

        except Exception as e:
            print(e)
            returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0}).to_dict()
            return jsonify(returnDTO)

    return wrapper
