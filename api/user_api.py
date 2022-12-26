from flask import Blueprint, request

from user_base import UserBase

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/create_user', methods=['POST'])
def user_creation():
    userbase = UserBase()
    return userbase.create_user(request)

@user_bp.route('/userlist', methods=['GET'])
def list_users():
    userbase = UserBase()
    return userbase.list_users()

@user_bp.route('/get_user', methods=['POST'])
def user_detail():
    userbase = UserBase()
    return userbase.describe_user(request)

@user_bp.route('/update_user', methods=['POST'])
def update_user():
    userbase = UserBase()
    return userbase.update_user(request)

@user_bp.route('/teams_user_list',methods=['POST'])
def get_list_user():
    userbase = UserBase()
    return userbase.list_team_users(request)

