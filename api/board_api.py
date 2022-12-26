from flask import Blueprint, request

from project_board_baase import ProjectBoardBase


board_bp = Blueprint('board_bp', __name__)

@board_bp.route('/create_board', methods=['POST'])
def user_creation():
    project_board_base = ProjectBoardBase()
    return project_board_base.create_board(request)

@board_bp.route('/add_task',methods=['POST'])
def add_task():
    project_board_base = ProjectBoardBase()
    return project_board_base.add_task(request)

@board_bp.route('/update_task',methods=['POST'])
def update_task():
    project_board_base = ProjectBoardBase()
    return project_board_base.update_task_status(request)

@board_bp.route('/list_boards',methods=['POST'])
def list_boards():
    project_board_base = ProjectBoardBase()
    return project_board_base.list_board(request)


@board_bp.route('/export_board',methods=['POST'])
def export_board():
    project_board_base = ProjectBoardBase()
    return project_board_base.export_board(request)



