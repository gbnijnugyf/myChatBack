from flask import Blueprint, request, jsonify, make_response
from datetime import datetime, timedelta
from src.application import db, cipher_suite
from src.models.DTO import ReturnDTO, SessionTextDTO, SessionRecordDTO, DataDTO

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

        # 进行数据库验证,若有该用户，ret该用户的id
        ret = db.sign_in(username, password)
        print(ret)
        pre_session_records = get_pre_session_records(ret)
        if ret == 0:  # 验证登录状态
            raise Exception("账号或密码错误")

        nextTime = datetime.now() + timedelta(seconds=120)
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
        session_texts = [SessionTextDTO(from_=text['is_ai'], text=text['message']).to_dict() for text in texts]

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
