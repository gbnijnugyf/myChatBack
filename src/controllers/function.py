from flask import Blueprint, jsonify, make_response, request
from libs.db import mysql
from models.DTO import ReturnDTO
from models.entity import Classification, FriendLink
from libs.similarity.model import semanticMatching

function = Blueprint("function", __name__)


@function.route("/search")
def Search():
    """搜索文章"""
    try:
        keyWord = str(request.args.get("word")).split(" ")

        # 所数据库中获取所有文章ID以及其标题
        dbObj = mysql()
        ret = dbObj.select_all_passage_id_and_title()
        dbObj.close()

        titleList = []  # 文章标题列表
        idList = []  # 文章ID列表
        for reti in ret:
            titleList.append(str(reti[1]))
            idList.append(int(reti[0]))

        retInd = semanticMatching(keyWord, titleList, 0.5)
        # print("keyWord results:", keyWord)
        # print("titleList results:", titleList)
        # print("search results:", retInd)

        data = []
        for retIndi in retInd:
            datai = {}
            datai["title"] = titleList[retIndi]
            datai["ID"] = idList[retIndi]
            data.append(datai)

        returnDTO = ReturnDTO.from_dict({"msg": "success", "status": 1}).to_dict()
        returnDTO["data"] = data
        return jsonify(returnDTO)
    except Exception as e:
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0}).to_dict()
        returnDTO["data"] = []
        return jsonify(returnDTO)


@function.route("/stat")
def Statistics():
    """网站统计"""
    try:
        return
    except Exception as e:
        return


@function.route("/flink")
def Flink():
    """友情链接"""
    try:
        # 数据库操作
        dbObj = mysql()
        ret = dbObj.select_flink()
        dbObj.close()

        # 数据处理
        data = []
        for reti in ret:
            flink = FriendLink()
            flink.name = reti[0]
            flink.description = reti[1]
            flink.url = reti[2]
            flink.cover = reti[3]
            data.append(
                {
                    "name": flink.name,
                    "description": flink.description,
                    "url": flink.url,
                    "cover": flink.cover,
                }
            )

        returnDTO = ReturnDTO.from_dict({"msg": "success", "status": 1}).to_dict()
        returnDTO["data"] = data
        return jsonify(returnDTO)
    except Exception as e:
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0}).to_dict()
        returnDTO["data"] = []
        return jsonify(returnDTO)


@function.route("/class")
def Class():
    """获取分类"""
    try:
        # 从数据库中获取所有分类
        dbObj = mysql()
        ret = dbObj.select_classes()
        dbObj.close()

        returnDTO = ReturnDTO.from_dict({"msg": "success", "status": 1}).to_dict()
        dataList = []
        for i in range(len(ret)):
            # 依次读取ret中的内容
            classObj = Classification()
            classObj.name = ret[i][0]
            classObj.description = ret[i][1]
            data = {
                "name": classObj.name,
                "description": classObj.description,
            }
            dataList.append(data)
        returnDTO["data"] = dataList
        return jsonify(returnDTO)

    except Exception as e:
        returnDTO = ReturnDTO.from_dict({"msg": str(e), "status": 0}).to_dict()
        returnDTO["data"] = []
        return jsonify(returnDTO)
