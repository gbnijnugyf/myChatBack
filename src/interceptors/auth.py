from application import app

from functools import wraps
from flask import request
from application import cipher_suite

from libs.db import mysql
from datetime import datetime

# @article.before_request
# @infoManager.before_request
# def infoManager_before_request():
#     pass

# @app.before_request
# def before_request():
#     app.logger.info("----------before_request----------")
#     return

# @app.after_request
# def after_request(response):
#     app.logger.warning("----------after_request----------")
#     return response


def secure(params: str):
    """对传入的参数进行处理,防止SQL注入"""
    pass


# 登录限制的装饰器 用于某些只让登录用户查看的网
# func是使用该修饰符的地方是视图函数页
def login_limit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        cookie = request.headers.get(app.config["AUTH_COOKIE_NAME"])
        if cookie == None:
            return func(*args, **kwargs, token=None, msg="登录信息失效")
        try:
            plain_text = cipher_suite.decrypt(cookie.encode("utf-8")).decode("utf-8")
        except Exception as e:
            return func(*args, **kwargs, token=None, msg="密文匹配失败")

        username = plain_text.split("-")[0]
        password = plain_text.split("-")[1]
        nextTime = plain_text.split("-")[2]
        nextTime = datetime.strptime(nextTime,"%Y#%m#%d#%H:%M:%S")
        if nextTime < datetime.now():
            return func(*args, **kwargs, token=None, msg="登录信息失效")

        # 进行数据库验证
        dbObj = mysql()
        ret = dbObj.checkPassword(username, password)
        dbObj.close()
        if ret == 0:  # 验证登录状态
            return func(*args, **kwargs, token=None, msg="账号或密码错误")

        return func(*args, **kwargs, token=cookie, msg="success")

    return wrapper
