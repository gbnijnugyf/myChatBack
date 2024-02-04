from flask import Blueprint

calendar = Blueprint("calendar", __name__)


@calendar.route("/page")
def Calendar():
    '''归档信息'''
    return "Hello world!"
