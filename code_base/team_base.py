from flask import jsonify
from marshmallow import Schema, fields, validates, ValidationError

from database.database import db
from database.flask_models import Team, User
from user_base import UserSchema



class AddRemoveUserSchema(Schema):
    id = fields.Integer(required=True)
    users = fields.List(fields.Integer, required=True)




class UpdateaTeamSchema(Schema):
    id = fields.Integer(required=True)
    team = fields.Nested(
        lambda: CreateTeamRequestSchema, required=True
    )




class CreateTeamRequestSchema(Schema):
    name = fields.Str(required=True, max_length=64)
    description = fields.Str(required=True, max_length=128)
    admin = fields.Integer(required=True)
    creation_time = fields.DateTime(dump_only=True)

    # @validates('name')
    # def validate_name(self, value):
    #     name = db.session.query(Team).filter(Team.name==value).first()
    #     if name:
    #         raise ValidationError('Team name must be unique')

class TeamBase:
    """
    Base interface implementation for API's to manage teams.
    For simplicity a single team manages a single project. And there is a separate team per project.
    Users can be
    """



    # create a team
    def create_team(self, request):
        """
        :param request: A json string with the team details
        {
          "name" : "<team_name>",
          "description" : "<some description>",
          "admin": "<id of a user>"
        }
        :return: A json string with the response {"id" : "<team_id>"}

        Constraint:
            * Team name must be unique
            * Name can be max 64 characters
            * Description can be max 128 characters
        """
        request_json = request.get_json()
        schema = CreateTeamRequestSchema()
        try:
            request_data = schema.load(request_json)
        except ValidationError as err:
            return jsonify({"error": err.messages}), 400
        existing_team = Team.query.filter_by(name=request_json['name']).first()
        if existing_team is not None:
            return jsonify({'error': 'Team name already exists'}), 400
        team = Team(**request_data)
        db.session.add(team)
        db.session.commit()
        return jsonify({'id': team.id}), 201

    def list_teams(self) -> str:
        """
        :return: A json list with the response.
        [
          {
            "name" : "<team_name>",
            "description" : "<some description>",
            "creation_time" : "<some date:time format>",
            "admin": "<id of a user>"
          }
        ]
        """
        teams = db.session.query(Team).all()
        create_team_request_schema = CreateTeamRequestSchema(many=True)
        teams_dict_list = create_team_request_schema.dump(teams)
        return jsonify(teams_dict_list)

    def update_team(self, request):
        """
        :param request: A json string with the team details
        {
          "id" : "<team_id>",
          "team" : {
            "name" : "<team_name>",
            "description" : "<team_description>",
            "admin": "<id of a user>"
          }
        }

        :return:

        Constraint:
            * Team name must be unique
            * Name can be max 64 characters
            * Description can be max 128 characters
        """
        update_team_schema = UpdateaTeamSchema(many=False)
        try:
            data = update_team_schema.load(request.get_json())
        except ValidationError as err:
            return jsonify({'error': err.messages}), 422

        # Extract the user details from the request body
        team_id = data.get("id")
        team = data.get("team")
        team_name = team.get("name")
        description = team.get("description")
        admin=team.get('admin')
        team = Team.query.get(team_id)
        if team is None or team.name != team_name:
            return jsonify({"error": "team name cannot be updated"}), 400
        team.description = description
        team.admin=admin
        db.session.commit()
        # Return a success response
        return "Team updated successfully", 200


    def add_users_to_team(self, request):
        """
        :param request: A json string with the team details
        {
          "id" : "<team_id>",
          "users" : ["user_id 1", "user_id2"]
        }

        :return:

        Constraint:
        * Cap the max users that can be added to 50
        """
        data = request.get_json()
        add_remove_user_schema=AddRemoveUserSchema()
        req_data=add_remove_user_schema.load(data)
        team_id=req_data['id']
        user_ids = req_data['users']
        if len(user_ids)>50:
            return jsonify({'error': 'more than 50 users not allowed'}), 404

        # Get the team from the database
        team = Team.query.get(team_id)
        if not team:
            # Return an error if the team does not exist
            return jsonify({'error': 'Team not found'}), 404

        # Get the list of user IDs from the request data


        # Update the users in the team
        users = User.query.filter(User.id.in_(user_ids)).all()
        for user in users:
            if user:
                team.users.append(user)


        # Commit the changes to the database
        db.session.commit()

        # Return a success message
        return jsonify({'message': 'Team updated successfully'})

    def remove_users_from_team(self,request):
        # Get the request data
        data = request.get_json()
        add_remove_user_schema = AddRemoveUserSchema()
        req_data = add_remove_user_schema.load(data)
        team_id = req_data['id']
        user_ids = req_data['users']
        # Get the team from the database
        team = Team.query.get(team_id)
        if not team:
            # Return an error if the team does not exist
            return jsonify({'error': 'Team not found'}), 404

        # Remove the users from the team
        users = User.query.filter(User.id.in_(user_ids)).all()
        for user in users:
            if user:
                team.users.remove(user)

        # Commit the changes to the database
        db.session.commit()

        # Return a success message
        return jsonify({'message': 'Users removed from team successfully'})

