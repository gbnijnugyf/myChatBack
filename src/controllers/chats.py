from flask import Blueprint, request, jsonify

from src.application import db
from src.interceptors.auth import cookie_check

chat = Blueprint("chat", __name__)


@chat.route("/add", methods=["POST"])
@cookie_check
def add(user_id):
    # 从请求中获取参数
    # id = request.json.get('id') 有cookie了，用cookie找到的user_id更好
    session_name = request.json.get('session_name')

    print(user_id, session_name)

    # 在数据库中插入对话框记录
    db.add_dialog(user_id, session_name)
    # 获取对话框ID
    dialogInfo = db.get_dialog(session_name)
    print(dialogInfo['dialog_id'])

    # 返回对话框ID
    return jsonify({"msg": "success", "status": 0, "data": {"session_id": dialogInfo['dialog_id']}})
