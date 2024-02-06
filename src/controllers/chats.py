import base64
from uuid import uuid4

from flask import Blueprint, request, jsonify

from src.application import db
from src.interceptors.auth import cookie_check

chat = Blueprint("chat", __name__)


@chat.route("/add", methods=["POST"])
@cookie_check
def addDialog(user_id):
    # 从请求中获取参数
    # id = request.json.get('id') 有cookie了，用cookie找到的user_id更好
    session_name = request.json.get('session_name')

    print(user_id, session_name)

    # 在数据库中插入对话框记录
    r = db.add_dialog(user_id, session_name)

    if not r:
        return jsonify({"msg": "add failed", "status": 1})
    else:
        # 获取对话框ID
        return jsonify({"msg": "success", "status": 0, "data": {"session_id": str(r)}})


@chat.route("/send", methods=["POST"])
@cookie_check
def sendMessage(user_id):
    # 从请求中获取参数
    # id = request.json.get('id') 有cookie了，用cookie找到的user_id更好
    session_id = request.json.get('session_id')
    text = request.json.get('text')
    image = request.json.get('image')

    hasImage = image is not None;
    # 在数据库中插入对话框记录
    text_id = db.add_text(session_id, False, hasImage, text)
    if not text_id:
        return jsonify({"msg": "add failed", "status": 1})

    if hasImage:
        # 图片转码
        # image = image_transcoding(image)
        # 生成路径
        path = "./static/userImages/" + str(uuid4()) + ".jpg"
        # 保存图片到本地
        save_image_from_base64(image, path)
        # 在数据库中插入图片记录
        r = db.add_image(session_id, text_id, path)
        if not r:
            if not db.delete_text(text_id):
                return jsonify({"msg": "rollback failed! bug!", "status": 1})

            return jsonify({"msg": "add images failed", "status": 1})

    # 模型生成回复
    reply = get_reply()
    # 在数据库中插入对话框记录
    reply_id = db.add_text(session_id, True, False, reply)
    if not reply_id:
        if not db.delete_text(text_id):
            return jsonify({"msg": "rollback failed! bug!", "status": 1})
        return jsonify({"msg": "add reply failed", "status": 1})

    # 返回对话框ID
    return jsonify({"msg": "success", "status": 0, "data": {"text": reply}})


@chat.route("/delete", methods=["DELETE"])
@cookie_check
def deleteDialog(user_id):
    # 从请求中获取参数
    # id = request.json.get('id') 有cookie了，用cookie找到的user_id更好
    session_id = request.args.get('session_id')

    # 在数据库中删除对话框记录
    r = db.delete_dialog(session_id)

    # 根据结果返回响应
    if r:
        return jsonify({"msg": "success", "status": 0, })
    else:
        return jsonify({"msg": "delete failed", "status": 1, })


# 连接模型生成回复，传入历史对话数组和最新图片
def get_reply():
    reply = ''
    # 模型处理......
    reply = '你好,我不是AI'

    return reply


# def image_transcoding(image_base64):
#     # 去除图片数据的前缀
#     # image_data = image_base64
#     image_data = image_base64.split(",")[1]
#     # 如果字符串长度不是4的倍数，添加等号
#     while len(image_data) % 4 != 0:
#         image_data += '='
#     print(image_data)
#     # 将Base64编码的图片数据转换为字节流
#     try:
#         image_bytes = base64.b64decode(image_data)
#     except Exception as e:
#         image_bytes = base64.urlsafe_b64decode(image_data)
#
#     return image_bytes


def save_image_from_base64(base64_string, file_path):
    base64_string = base64_string.split(",")[-1]  # 删除数据URI的前缀
    while len(base64_string) % 4 != 0:
        base64_string += '='
    image_data = base64.b64decode(base64_string)
    with open(file_path, 'wb') as f:
        f.write(image_data)
