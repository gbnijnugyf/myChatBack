import base64
import os
from uuid import uuid4

from flask import Blueprint, request, jsonify, make_response
from datetime import datetime, timedelta
from src.application import db, cipher_suite
from src.interceptors.auth import cookie_check
from src.models.DTO import ReturnDTO, SessionTextDTO, SessionRecordDTO, DataDTO

user = Blueprint("user", __name__)


@user.route("/login", methods=["POST"])
# @cookie_check
def login():
    try:
        username = str(request.json.get("name"))
        password = str(request.json.get("password"))
        print(username, password)
        if "-" in username or "-" in password:
            raise Exception("账号或密码中不得出现特殊字符")

        # 进行数据库验证,若有该用户，ret该用户的id
        ret = db.sign_in(username, password)
        print(ret)
        pre_session_records = get_pre_session_records(ret)
        if ret == 0:  # 验证登录状态
            raise Exception("账号或密码错误")

        nextTime = datetime.now() + timedelta(seconds=1200)  # 1200秒后失效
        message = "{}-{}-{}".format(
            username, password, nextTime.strftime("%Y#%m#%d#%H:%M:%S")
        ).encode("utf-8")
        cipher_text = cipher_suite.encrypt(message)

        returnDTO = ReturnDTO.from_dict({"msg": "success", "status": 1}).to_dict()
        # data = {"id": ret, "sign": cipher_text.decode("utf-8"), "pre_session_records": pre_session_records}
        data = DataDTO(id=str(ret), sign=cipher_text.decode("utf-8"), pre_session_records=pre_session_records).to_dict()
        returnDTO["data"] = data
        response = make_response(jsonify(returnDTO))
        # response.headers['Access-Control-Expose-Headers'] = "*"
        print(cipher_text.decode("utf-8"))

        return response
    except Exception as e:
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0}).to_dict()
        return jsonify(returnDTO)


def get_pre_session_records(user_id):
    # 获取与给定用户相关的所有对话框
    dialogs = db.get_dialogs(user_id)

    # 用于存储SessionRecordDTO对象的列表
    pre_session_records = []

    for dialog in dialogs:
        # 获取与当前对话框相关的所有文本
        texts = db.get_texts(dialog['dialog_id'])

        # 构造SessionTextDTO对象
        session_texts = []
        for text in texts:
            if text['has_img'] == 1:
                imgPath = db.get_image(text['text_id'])
                img = image_to_base64(imgPath);
                # save_image_to_file(img, f"./static/userImages/" + str(uuid4()) + ".jpg")
            else:
                img = None

            session_texts.append(SessionTextDTO(from_=text['is_ai'], text=text['message'], image=img).to_dict())

        # 构造SessionTextDTO对象
        # session_texts = [SessionTextDTO(from_=text['is_ai'], text=text['message'],
        #                                 img=db.get_image_as_base64(text['text_id'])).to_dict() for text in texts]

        # 构造SessionRecordDTO对象
        record = SessionRecordDTO(
            session_id=str(dialog['dialog_id']),
            session_date=str(dialog['time']),
            session_texts=session_texts,
            session_name=dialog['name']
        )

        # 将SessionRecordDTO对象添加到列表中
        pre_session_records.append(record.to_dict())

    return pre_session_records


def image_to_base64(file_path):
    with open(file_path, 'rb') as f:
        image_data = f.read()
    base64_string = base64.b64encode(image_data).decode()
    return 'data:image/jpeg;base64,' + base64_string

# def save_image_to_file(image_data, file_path):
#     if image_data is not None:
#         with open(file_path, 'wb') as file:
#             file.write(base64.b64decode(image_data))
