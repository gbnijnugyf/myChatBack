from flask import Blueprint

about = Blueprint("about", __name__)


@about.route("/page")
def About():
    '''关于信息'''
    try:
        return
    except Exception as e:
        return
