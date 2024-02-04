from datetime import datetime
from flask import Blueprint, jsonify, redirect, request, url_for
from functools import wraps
from libs.pic import getCommentAvatorURL
from models.entity import CommentEntity
from models.DTO import CommentDTO, ReturnDTO
from application import hostname
from libs.db import mysql
from libs.mail.mail import send_response
from application import app, cipher_suite

comment = Blueprint("comment", __name__)


@comment.route("/pagecom")
def Comment():
    """获取某一文章的评论"""
    try:
        passageID = str(request.args.get("id"))

        # 数据库
        dbObj = mysql()
        ret = dbObj.select_all_comment(passageID)
        dbObj.close()

        # 对ret进行处理
        rootList = []
        replyDict = {}
        mapList = {}

        for reti in ret:
            mapList[int(reti[9])] = int(reti[7])

        for reti in ret:
            if int(reti[7]) == 0:
                # 根评论
                rootList.append(reti)
            else:
                # 回复评论
                # 判断当前回复的父评论是否是根评论
                comid = int(reti[9])
                while mapList[comid] != 0:
                    comid = mapList[comid]
                if replyDict.get(comid):
                    # 回复字典内存在该根评论的键
                    replyDict[comid].append(reti)
                else:
                    replyDict[comid] = [reti]

        data = []
        for rootItem in rootList:
            dataItem = {}
            rootComment = {}
            reply = []

            # 根评论处理
            rootComment["primary"] = int(rootItem[0])
            rootComment["isBlogger"] = int(rootItem[1])
            rootComment["nickname"] = str(rootItem[2])
            rootComment["email"] = str(rootItem[3])
            rootComment["body"] = rootItem[4].decode("utf-8")
            rootComment["avator_url"] = EmailAvatorUrlHandler(
                rootItem[5].decode("utf-8")
            )
            rootComment["passageID"] = int(rootItem[6])
            rootComment["preID"] = 0
            rootComment["time"] = rootItem[8].strftime("%Y-%m-%d %H:%M:%S")
            rootComment["commentID"] = int(rootItem[9])
            dataItem["rootComment"] = rootComment

            # 回复评论处理
            if replyDict.get(int(rootItem[9])):
                # 当前根评论存在回复评论
                for replyi in replyDict[int(rootItem[9])]:
                    replyItem = {}
                    replyItem["primary"] = int(replyi[0])
                    replyItem["isBlogger"] = int(replyi[1])
                    replyItem["nickname"] = str(replyi[2])
                    replyItem["email"] = str(replyi[3])
                    replyItem["body"] = replyi[4].decode("utf-8")
                    replyItem["avator_url"] = EmailAvatorUrlHandler(
                        replyi[5].decode("utf-8")
                    )
                    replyItem["passageID"] = int(replyi[6])
                    replyItem["preID"] = int(replyi[7])
                    replyItem["time"] = replyi[8].strftime("%Y-%m-%d %H:%M:%S")
                    replyItem["commentID"] = int(replyi[9])
                    reply.append(replyItem)
            dataItem["reply"] = reply
            data.append(dataItem)

        returnDTO = ReturnDTO.from_dict({"msg": "success", "status": 1}).to_dict()
        returnDTO["data"] = data
        return jsonify(returnDTO)
    except Exception as e:
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0}).to_dict()
        returnDTO["data"] = []
        return jsonify(returnDTO)


@comment.route("/message")
def Message():
    """获取留言"""
    try:
        # 数据库
        dbObj = mysql()
        ret = dbObj.select_all_message()
        dbObj.close()

        # 对ret进行处理
        rootList = []
        replyDict = {}
        mapList = {}

        for reti in ret:
            mapList[int(reti[9])] = int(reti[7])

        for reti in ret:
            if int(reti[7]) == 0:
                # 根评论
                rootList.append(reti)
            else:
                # 回复评论
                # 判断当前回复的父评论是否是根评论
                comid = int(reti[9])
                while mapList[comid] != 0:
                    comid = mapList[comid]
                if replyDict.get(comid):
                    # 回复字典内存在该根评论的键
                    replyDict[comid].append(reti)
                else:
                    replyDict[comid] = [reti]

        data = []
        for rootItem in rootList:
            dataItem = {}
            rootComment = {}
            reply = []

            # 根评论处理
            rootComment["primary"] = int(rootItem[0])
            rootComment["isBlogger"] = int(rootItem[1])
            rootComment["nickname"] = str(rootItem[2])
            rootComment["email"] = str(rootItem[3])
            rootComment["body"] = rootItem[4].decode("utf-8")
            rootComment["avator_url"] = EmailAvatorUrlHandler(
                rootItem[5].decode("utf-8")
            )
            rootComment["passageID"] = None
            rootComment["preID"] = 0
            rootComment["time"] = rootItem[8].strftime("%Y-%m-%d %H:%M:%S")
            rootComment["commentID"] = int(rootItem[9])
            dataItem["rootComment"] = rootComment

            # 回复评论处理
            if replyDict.get(int(rootItem[9])):
                # 当前根评论存在回复评论
                for replyi in replyDict[int(rootItem[9])]:
                    replyItem = {}
                    replyItem["primary"] = int(replyi[0])
                    replyItem["isBlogger"] = int(replyi[1])
                    replyItem["nickname"] = str(replyi[2])
                    replyItem["email"] = str(replyi[3])
                    replyItem["body"] = replyi[4].decode("utf-8")
                    replyItem["avator_url"] = EmailAvatorUrlHandler(
                        replyi[5].decode("utf-8")
                    )
                    replyItem["passageID"] = None
                    replyItem["preID"] = int(replyi[7])
                    replyItem["time"] = replyi[8].strftime("%Y-%m-%d %H:%M:%S")
                    replyItem["commentID"] = int(replyi[9])
                    reply.append(replyItem)
            dataItem["reply"] = reply
            data.append(dataItem)

        returnDTO = ReturnDTO.from_dict({"msg": "success", "status": 1}).to_dict()
        returnDTO["data"] = data
        return jsonify(returnDTO)
    except Exception as e:
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0}).to_dict()
        returnDTO["data"] = []
        return jsonify(returnDTO)


def IsBlogger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        cookie = request.headers.get(app.config["AUTH_COOKIE_NAME"])
        if cookie == None:
            return func("visitor")
        try:
            plain_text = cipher_suite.decrypt(cookie.encode("utf-8")).decode("utf-8")
        except Exception as e:
            return func("visitor")

        username = plain_text.split("-")[0]
        password = plain_text.split("-")[1]
        nextTime = plain_text.split("-")[2]
        nextTime = datetime.strptime(nextTime, "%Y#%m#%d#%H:%M:%S")
        if nextTime < datetime.now():
            return func("visitor")

        # 进行数据库验证
        dbObj = mysql()
        ret = dbObj.checkPassword(username, password)
        dbObj.close()
        if ret == 0:  # 验证登录状态
            return func("visitor")

        return func("blogger")

    return wrapper


@comment.route("/add", methods=["POST"])
@IsBlogger
def Add(who):
    """管理员/访客添加评论/留言"""
    try:
        primary = str(request.json.get("primary"))
        passageID = str(request.json.get("passageID"))
        preID = request.json.get("preID")  # 可为空
        nickname = str(request.json.get("nickname"))
        email = str(request.json.get("email"))  # 正则表达式验证
        body = str(request.json.get("body"))
        if who == "visitor":  # 判断是否博主
            isBlogger = 0
        elif who == "blogger":
            isBlogger = 1

        # 验证数据正确性
        comment = CommentEntity()  # 自动生成时间
        comment.primary = primary
        comment.passage_id = passageID
        comment.pre_id = preID
        comment.nickname = nickname
        comment.email = email  # 验证邮箱正确性
        comment.body = body
        comment.is_blogger = isBlogger

        # 若为qq邮箱，则获取其头像
        if email.split("@")[1] == "qq.com":
            qq = email.split("@")[0]
            comment.avator_url = "https://q.qlogo.cn/g?b=qq&nk=" + qq + "&s=100"
        else:
            comment.avator_url = getCommentAvatorURL()

        # 插入数据库，并得到返回的评论ID
        dbObj = mysql()
        if preID == "" or preID == None:
            ret = dbObj.insert_comment(
                comment.primary,
                comment.is_blogger,
                comment.nickname,
                comment.email,
                comment.body,
                comment.avator_url,
                comment.passage_id,
            )
        else:
            ret = dbObj.insert_comment(
                comment.primary,
                comment.is_blogger,
                comment.nickname,
                comment.email,
                comment.body,
                comment.avator_url,
                comment.passage_id,
                comment.pre_id,
            )
            # 获取被回复的评论的内容和优先
            mailInfo = dbObj.select_comment(preID)

            # 发送回复邮件
            # print(type(mailInfo[1]),mailInfo[1])
            # print(type(mailInfo[0].decode('utf-8')),mailInfo[0].decode('utf-8'))
            # print(body)
            # print('成功发送回复邮件')
            send_response(
                recipients=[mailInfo[1]],
                comment=mailInfo[0].decode("utf-8"),
                response=body,
                replyer=nickname,
            )

        dbObj.close()

        # 返回数据封装
        commentDTO = CommentDTO.from_dict(
            {
                "primary": comment.primary,
                "passageID": comment.passage_id,
                "commentID": ret[0],
                "email": comment.email,
                "isBlogger": comment.is_blogger,
                "nickname": comment.nickname,
                "preID": comment.pre_id,
                "body": comment.body,
                "avator_url": EmailAvatorUrlHandler(comment.avator_url),
                "time": ret[1].strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        returnDTO = ReturnDTO.from_dict({"msg": "success", "status": 1}).to_dict()
        returnDTO["data"] = commentDTO.to_dict()
        return jsonify(returnDTO)

    except Exception as e:
        # 返回数据封装
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0}).to_dict()
        returnDTO["data"] = {}
        return jsonify(returnDTO)


# login验证
@comment.route("/delete")
def Delete():
    """管理员删除评论/留言"""
    try:
        commentID = str(request.args.get("id"))

        # 进行数据库操作
        dbObj = mysql()
        dbObj.delete_comment(commentID)
        dbObj.close()

        returnDTO = ReturnDTO.from_dict({"msg": "success", "status": 1}).to_dict()
        return jsonify(returnDTO)
    except Exception as e:
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0}).to_dict()
        return jsonify(returnDTO)


def EmailAvatorUrlHandler(url):
    if url.split("=")[0] == "https://q.qlogo.cn/g?b":
        ret = url
    else:
        ret = hostname + url
    return ret
