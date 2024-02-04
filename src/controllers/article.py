import base64
from flask import Blueprint, request, jsonify
from datetime import datetime

# from interceptors.auth import login_limit
from uuid import uuid4
import os
from application import hostname

from models.DTO import ReturnDTO
from models.DTO import ImgUploadDTO, ArticleListDTO, ArticleDTO
from models.entity import Article
from libs import pic
from libs.db import mysql


article = Blueprint("article", __name__)


@article.route("/vlist", methods=["GET"])
def ArticleListClassifiedVisible():
    """分类对应分类-可见-文章列表"""
    try:
        classname = str(request.args.get("classname"))

        # 从数据库中获取某一分类的
        dbObj = mysql()
        if classname == "all":
            # 提取所有可见文章列表
            ret = dbObj.all_visible_article()
        else:
            # 提取某一分类可见文章列表
            ret = dbObj.articale_classifed_visible(classname)
        dbObj.close()

        returnDTO = ReturnDTO.from_dict({"msg": "success", "status": 1}).to_dict()
        dataList = []
        for i in range(len(ret)):
            # 依次读取ret中的内容
            articleObj = Article()
            articleObj.ID = ret[i][0]
            articleObj.title = ret[i][1]
            articleObj.cover = ret[i][2].decode("utf-8")
            articleObj.releaseTime = ret[i][3].strftime("%Y-%m-%d %H:%M:%S")
            articleObj.visibility = ret[i][4]
            data = {
                "ID": articleObj.ID,
                "title": articleObj.title,
                "cover": hostname + articleObj.cover,
                "releaseTime": articleObj.releaseTime,
                "visibility": articleObj.visibility,
            }
            dataList.append(data)
        returnDTO["data"] = dataList
        return jsonify(returnDTO)

    except Exception as e:
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0}).to_dict()
        returnDTO["data"] = []
        return jsonify(returnDTO)


# 需要加上login_limit
@article.route("/list", methods=["GET"])
def ArticleListClassified():
    """分类对应分类-所有-文章列表(管理员专用)"""
    try:
        classname = str(request.args.get("classname"))

        # 从数据库中获取某一分类的
        dbObj = mysql()
        if classname == "all":
            # 提取所有文章列表
            ret = dbObj.all_article()
        else:
            # 提取某一分类文章列表
            ret = dbObj.select_passage_by_classification(classname)
        dbObj.close()

        returnDTO = ReturnDTO.from_dict({"msg": "success", "status": 1}).to_dict()
        dataList = []
        for i in range(len(ret)):
            # 依次读取ret中的内容
            articleObj = Article()
            articleObj.ID = ret[i][0]
            articleObj.title = ret[i][1]
            articleObj.cover = ret[i][2].decode("utf-8")
            articleObj.releaseTime = ret[i][3].strftime("%Y-%m-%d %H:%M:%S")
            articleObj.visibility = ret[i][4]
            data = {
                "ID": articleObj.ID,
                "title": articleObj.title,
                "cover": hostname + articleObj.cover,
                "releaseTime": articleObj.releaseTime,
                "visibility": articleObj.visibility,
            }
            dataList.append(data)
        returnDTO["data"] = dataList
        return jsonify(returnDTO)

    except Exception as e:
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0}).to_dict()
        returnDTO["data"] = []
        return jsonify(returnDTO)


@article.route("/page", methods=["GET"])
def Page():
    """文章页面详细内容(已完成测试)"""
    try:
        articleID = str(request.args.get("id"))

        # 从数据库中检索id的文章
        articleObj = Article()
        dbObj = mysql()
        ret = dbObj.select_passage(articleID)
        dbObj.close()
        articleObj.ID = ret[0]
        articleObj.title = ret[1]
        articleObj.cover = ret[2].decode("utf-8")
        articleObj.releaseTime = ret[3].strftime("%Y-%m-%d %H:%M:%S")
        articleObj.classification = ret[4]
        articleObj.body = ret[5].decode("utf-8")
        articleObj.visibility = ret[6]

        returnDTO = ReturnDTO.from_dict({"msg": "success", "status": 1}).to_dict()
        articleDTO = ArticleDTO.from_dict(
            {
                "id": articleObj.ID,
                "title": articleObj.title,
                "cover": hostname + articleObj.cover,
                "releaseTime": articleObj.releaseTime,
                "classification": articleObj.classification,
                "body": articleObj.body,
                "visibility": articleObj.visibility,
            }
        )
        returnDTO["data"] = articleDTO.to_dict()
        return jsonify(returnDTO)

    except Exception as e:
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0}).to_dict()
        returnDTO["data"] = {}
        return jsonify(returnDTO)


@article.route("/publish", methods=["POST"])
def Publish():
    """管理员发布文章(已完成测试)"""
    try:
        articleObj = Article()  # 自动生成文章的保存时间
        articleObj.title = str(request.json.get("title"))
        articleObj.classification = str(request.json.get("classification"))
        articleObj.body = str(request.json.get("body"))

        ID = request.json.get("ID")
        if ID == "" or ID == None:
            # 新增的文章数据
            raise Exception("文章ID不能为空")
            # newPas = True
        else:
            # 更新原有的文章数据
            articleObj.ID = ID
            newPas = False

        cover = request.json.get("cover")
        if cover == "" or cover == None:
            # 博主未上传缩略图/封面
            articleObj.cover = pic.getPageCover()
        else:
            # 博主上传缩略图/封面
            # base64解码
            fileName = "../static/cover/" + str(uuid4()) + ".jpg"
            cover = cover.split(",")[1]
            with open(fileName, "wb") as file:
                img = base64.b64decode(cover)
                file.write(img)
            articleObj.cover = fileName[2:]

        # 进行数据更新
        dbObj = mysql()
        if newPas:
            ret = dbObj.create_passage(
                articleObj.title,
                articleObj.classification,
                articleObj.body,
                articleObj.cover,
                visibility=1,
            )
            articleObj.ID = ret[0]
            articleObj.releaseTime = ret[1].strftime("%Y-%m-%d %H:%M:%S")
        else:
            ret = dbObj.update_passage(
                articleObj.ID,
                articleObj.title,
                articleObj.classification,
                articleObj.body,
                articleObj.cover,
            )
            dbObj.release_passage(articleObj.ID)
            articleObj.releaseTime = ret.strftime("%Y-%m-%d %H:%M:%S")
        dbObj.close()

        returnDTO = ReturnDTO.from_dict({"msg": "success", "status": 1}).to_dict()
        returnDTO["data"] = {"id": articleObj.ID, "releaseTime": articleObj.releaseTime}
        return jsonify(returnDTO)

    except Exception as e:
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0}).to_dict()
        returnDTO["data"] = []
        return jsonify(returnDTO)


@article.route("/unpublish", methods=["GET"])
def Unpublish():
    """管理员取消发布文章(已完成测试)"""
    try:
        articleObj = Article(id_=request.args.get("id"))

        # 把数据库中该id对应的文章的状态改为未发布
        dbObj = mysql()
        dbObj.cancel_release(articleObj.ID)
        dbObj.close()

        returnDTO = ReturnDTO.from_dict({"msg": "success", "status": 1}).to_dict()
        return jsonify(returnDTO)

    except Exception as e:
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0}).to_dict()
        return jsonify(returnDTO)


@article.route("/edit", methods=["PUT"])
def Edit():
    """管理员保存编辑文章(已完成测试)"""
    try:
        articleObj = Article()  # 自动生成文章的保存时间
        articleObj.title = str(request.json.get("title"))
        articleObj.classification = str(request.json.get("classification"))
        articleObj.body = str(request.json.get("body"))
        articleObj.visibility = str(request.json.get("visibility"))

        ID = request.json.get("ID")
        if ID == "" or ID == None:
            # 新增的文章数据
            newPas = True
        else:
            # 更新原有的文章数据
            articleObj.ID = ID
            newPas = False

        cover = request.json.get("cover")
        if cover == "" or cover == None:
            # 博主未上传缩略图/封面
            articleObj.cover = pic.getPageCover()
        else:
            # 博主上传缩略图/封面
            # base64解码
            fileName = "../static/cover/" + str(uuid4()) + ".jpg"
            with open(fileName, "wb") as file:
                img = base64.b64decode(cover)
                file.write(img)
            articleObj.cover = fileName[2:]

        # 进行数据更新
        dbObj = mysql()
        if newPas:
            ret = dbObj.create_passage(
                articleObj.title,
                articleObj.classification,
                articleObj.body,
                articleObj.cover,
            )
            articleObj.ID = ret[0]
            articleObj.releaseTime = ret[1].strftime("%Y-%m-%d %H:%M:%S")
        else:
            ret = dbObj.update_passage(
                articleObj.ID,
                articleObj.title,
                articleObj.classification,
                articleObj.body,
                articleObj.cover,
            )
            articleObj.releaseTime = ret.strftime("%Y-%m-%d %H:%M:%S")
        dbObj.close()

        returnDTO = ReturnDTO.from_dict({"msg": "success", "status": 1}).to_dict()
        returnDTO["data"] = {"id": articleObj.ID, "releaseTime": articleObj.releaseTime}
        return jsonify(returnDTO)

    except Exception as e:
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0}).to_dict()
        returnDTO["data"] = {}
        return jsonify(returnDTO)


@article.route("/imgUpload", methods=["POST"])
# @login_limit
def imgUpload():
    try:
        file = request.files["file"]

        fname = file.filename
        ext = fname.rsplit(".")[-1]

        ext_allowed = ["png", "jpg", "jpeg", "bmp"]
        if ext not in ext_allowed:
            raise Exception("Extensions not allowed")

        fileName = str(uuid4()) + "." + ext  # 生成一个uuid作为文件名
        filePath = os.path.join("../static/uploadImg/", fileName)
        file.save(filePath)

        # 返回数据封装
        iuDTO = ImgUploadDTO.from_dict(
            {"url": hostname + "/static/uploadImg/" + fileName}
        )
        returnDTO = ReturnDTO.from_dict({"msg": "success", "status": 1}).to_dict()
        returnDTO["data"] = iuDTO.to_dict()
        return jsonify(returnDTO)

    except Exception as e:
        # 返回数据封装
        iuDTO = ImgUploadDTO.from_dict({"url": ""})
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0}).to_dict()
        returnDTO["data"] = iuDTO.to_dict()
        return jsonify(returnDTO)


@article.route("/delete", methods=["DELETE"])
def Delete():
    """管理员删除文章"""
    try:
        articleID = str(request.args.get("id"))

    except Exception as e:
        pass
