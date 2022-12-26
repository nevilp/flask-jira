from flask import Blueprint, request

from team_base import TeamBase


team_bp = Blueprint('team_bp', __name__)

@team_bp.route('/create_team', methods=['POST'])
def user_creation():
    teambase = TeamBase()
    return teambase.create_team(request)

@team_bp.route('/team_list', methods=['GET'])
def list_team():
    teambase = TeamBase()
    return teambase.list_teams()

@team_bp.route('/update_team', methods=['POST'])
def update_team():
    teambase = TeamBase()
    return teambase.update_team(request)

@team_bp.route('/add_user_to_team', methods=['PATCH'])
def add_user_to_team():
    teambase = TeamBase()
    return teambase.add_users_to_team(request)

@team_bp.route('/remove_user_from_team', methods=['POST'])
def remove_user_from_team():
    teambase = TeamBase()
    return teambase.remove_users_from_team(request)


