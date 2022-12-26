from flask import Blueprint, request



from api.bueprint_api import team_bp
from code_base.swagger_setup import swagger
from code_base.team_base import TeamBase


@team_bp.route('/create_team', methods=['POST'])
@swagger.docs
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


