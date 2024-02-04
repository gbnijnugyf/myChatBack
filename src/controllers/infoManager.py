from flask import Blueprint, make_response, request, jsonify
from application import app
from interceptors.auth import login_limit
from libs.pic import getFLCover
from models.DTO import ReturnDTO
from libs.db import mysql


infoManager = Blueprint("infoManager", __name__)


@infoManager.route("/addC", methods=["POST"])
@login_limit
def AddC(token, msg):
    """管理员添加分类(完成测试)"""
    try:
        if token == None:
            raise Exception(msg)

        class_name = str(request.json.get("name"))
        class_description = str(request.json.get("description"))

        # 写入数据库
        dbObj = mysql()
        dbObj.insert_classification(class_name, class_description)
        dbObj.close()

        returnDTO = ReturnDTO.from_dict({"msg": "success", "status": 1})

        response = make_response(jsonify(returnDTO.to_dict()))
        response.delete_cookie(app.config["AUTH_COOKIE_NAME"])
        response.set_cookie(
            app.config["AUTH_COOKIE_NAME"], token, max_age=60 * 60, httponly=True
        )

        return response

    except Exception as e:
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0})
        return jsonify(returnDTO.to_dict())


@infoManager.route("/addF", methods=["POST"])
def AddF():
    """管理员添加友链"""
    try:
        fl_name = str(request.json.get("name"))
        fl_description = str(request.json.get("description"))
        fl_url = str(request.json.get("url"))
        fl_cover = str(request.json.get("cover"))
        if fl_cover == "":
            fl_cover = getFLCover()

        # 写入数据库

        return
    except Exception as e:
        return


@infoManager.route("/editC", methods=["PUT"])
def EditC():
    """管理员编辑分类"""
    try:
        old_class_name = str(request.json.get("oldname"))
        class_name = str(request.json.get("name"))
        class_description = str(request.json.get("description"))

        # 写入数据库
        dbObj = mysql()
        dbObj.update_classification(old_class_name, class_name, class_description)
        dbObj.close()

        returnDTO = ReturnDTO.from_dict({"msg": "success", "status": 1})
        return jsonify(returnDTO.to_dict())

    except Exception as e:
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0})
        return jsonify(returnDTO.to_dict())


@infoManager.route("/editF", methods=["PUT"])
def EditF():
    """管理员编辑友链"""
    try:
        fl_name = str(request.json.get("name"))
        fl_description = str(request.json.get("description"))
        fl_url = str(request.json.get("url"))
        fl_cover = request.json.get("cover")
        if fl_cover == "" or fl_cover == None:
            fl_cover = getFLCover()

        # 写入数据库

        return
    except Exception as e:
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0})
        return jsonify(returnDTO.to_dict())


@infoManager.route("/delete", methods=["DELETE"])
def Delete():
    """管理员删除友链/分类"""
    try:
        infoName = str(request.args.get("name"))
        infoType = str(request.args.get("type"))

        # 进行相应的数据库操作

        return
    except Exception as e:
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0})
        return jsonify(returnDTO.to_dict())
