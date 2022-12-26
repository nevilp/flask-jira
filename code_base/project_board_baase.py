
import os
from datetime import datetime

import pandas as pd
from flask import jsonify, json, send_file
from marshmallow import Schema, fields, ValidationError
from tabulate import tabulate

from database.database import db
from database.flask_models import Board, Task, User


class TaskSchema(Schema):
    title = fields.Str(required=True, max_length=64)
    description = fields.Str(max_length=128)
    user_id = fields.Int(required=True)
    creation_time = fields.DateTime(dump_only=True,required=True)
    board_id = fields.Int(required=True)

class TaskStatusSchema(Schema):
    id = fields.Int(required=True)
    status = fields.Str(required=True, validate=lambda s: s in ['OPEN', 'IN_PROGRESS', 'COMPLETE'])

class BoardSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class CreateBoardRequestSchema(Schema):
    name = fields.Str(required=True, max_length=64)
    description = fields.Str(required=True, max_length=128)
    team_id = fields.Int(required=True)



class ProjectBoardBase:
    """
    A project board is a unit of delivery for a project. Each board will have a set of tasks assigned to a user.
    """

    # create a board
    def create_board(self, request):
        """
        :param request: A json string with the board details.
        {
            "name" : "<board_name>",
            "description" : "<description>",
            "team_id" : "<team id>"
            "creation_time" : "<date:time when board was created>"
        }
        :return: A json string with the response {"id" : "<board_id>"}

        Constraint:
         * board name must be unique for a team
         * board name can be max 64 characters
         * description can be max 128 characters
        """
        schema = CreateBoardRequestSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError  as errors:
            return jsonify(errors), 400
        name = data['name']
        description = data['description']
        team_id = data['team_id']
        creation_time = datetime.utcnow()
        board = Board(name=name, description=description, team_id=team_id, creation_time=creation_time)
        try:
            db.session.add(board)
            db.session.commit()
        except Exception as e:
            return jsonify({'error': str(e)}), 400
        return jsonify({'id': board.id}), 201

    def add_task(self, request: str) -> str:
        """
        :param request: A json string with the task details. Task is assigned to a user_id who works on the task
        {
            "title" : "<board_name>",
            "description" : "<description>",
            "user_id" : "<team id>"
            "creation_time" : "<date:time when task was created>"
        }
        :return: A json string with the response {"id" : "<task_id>"}

        Constraint:
         * task title must be unique for a board
         * title name can be max 64 characters
         * description can be max 128 characters

        Constraints:
        * Can only add task to an OPEN board
        """
        # Parse and validate the request data
        data = request.get_json()
        schema = TaskSchema()
        try:
            task_data= schema.load(data)
        except ValidationError as errors:
            return jsonify({'error': errors}), 400

        # Check if the board is open
        board = Board.query.filter_by(id=task_data['board_id']).first()
        if not board:
            return jsonify({'error': 'Board not found'}), 404
        if board.status != 'OPEN':
            return jsonify({'error': 'Cannot add task to closed board'}), 400

        # Create the task
        task = Task(title=task_data['title'], description=task_data['description'], user_id=task_data['user_id'],
                    creation_time=datetime.utcnow(), board_id=board.id)
        db.session.add(task)
        db.session.commit()

        return jsonify({'id': task.id}), 201

    def update_task_status(self, request: str):
        """
        :param request: A json string with the user details
        {
            "id" : "<task_id>",
            "status" : "OPEN | IN_PROGRESS | COMPLETE"
        }
        """

        data = request.get_json()
        schema = TaskStatusSchema()
        try:
            task_data = schema.load(data)
        except ValidationError as errors:
            return jsonify({'error': errors}), 400

        # Check if the task exists
        task = Task.query.get(task_data['id'])
        if not task:
            return jsonify({'error': 'Task not found'}), 404

        # Update the task status
        task.status = task_data['status']
        db.session.commit()

        return jsonify({'status': 'success'}), 200


    def list_board(self,request):
        # Parse and validate the request data
        data = request.get_json()
        team_id=data['team_id']
        # Get the boards for the team
        boards = Board.query.filter_by(team_id=team_id).all()
        if not boards:
            return jsonify({'error': 'No boards found for the team'}), 404
        # Serialize the boards
        schema = BoardSchema(many=True)
        result = schema.dump(boards)
        return jsonify(result), 200

    def export_board(self,request):
        json_data = json.loads(request.data)
        id = json_data['id']
        # df=pd.read_sql(db.session.query(Task.id,Task.title,User.name,Task.status).filter(Task.board_id==id).\
        #     join(User,User.id==Task.user_id).statement,db.engine)
        df = pd.read_sql(db.session.query(Task.id, Task.title, User.user_name, Task.status).filter(Task.board_id == id). \
                         join(User, User.id == Task.user_id).statement, db.engine)
        df['task'] = df['id'].map(str) + '-->' + df['title'] + '(' + df['user_name'] + ')'
        df = df[['task', 'status']]
        df = df.pivot(columns='status', values='task')
        df = df.reindex(columns=['OPEN', 'IN_PROGRESS', 'COMPLETE'],fill_value=None)
        df = df.fillna('')
        file_path = os.path.abspath("../out/board_{}.txt".format(id))
        print(file_path)


        with open(file_path, 'w') as the_file:
            the_file.write(tabulate(df, headers='keys', showindex=False, tablefmt='psql'))
            # Check if the file exists
            if not os.path.exists(file_path):
                return jsonify({'error': 'File not found'}), 404
        return send_file(file_path,mimetype='text/plain')



