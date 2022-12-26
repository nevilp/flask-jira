from flask import request, jsonify, Blueprint



from marshmallow import Schema, fields, validate, ValidationError

from database.database import db
from database.flask_models import User, Team


class UpdateUserSchema(Schema):
    id = fields.Integer(required=True)
    user = fields.Nested(
        lambda: UserSchema, required=True
    )


class UserSchema(Schema):
    user_name = fields.String(required=True, validate=validate.Length(max=64))
    display_name = fields.String(required=True, validate=validate.Length(max=64))
    creation_time = fields.DateTime(dump_only=True)

class TeamUserSchema(Schema):
    id=fields.Integer(dump_only=True)
    user_name = fields.String(required=True, validate=validate.Length(max=64))
    display_name = fields.String(required=True, validate=validate.Length(max=64))
    creation_time = fields.DateTime(dump_only=True)

class UserBase():

    def create_user(self,request):
        """
                :param request: A json string with the user details
                {
                  "name" : "<user_name>",
                  "display_name" : "<display name>"
                }
                :return: A json string with the response {"id" : "<user_id>"}

                Constraint:
                    * user name must be unique
                    * name can be max 64 characters
                    * display name can be max 64 characters
                """
        user_data = request.get_json()
        user_schema = UserSchema()
        try:
            user_data = user_schema.load(user_data)
        except ValidationError as err:
            return jsonify({'error': err.messages}), 422
        existing_user = User.query.filter_by(user_name=user_data['user_name']).first()
        if existing_user is not None:
            return jsonify({'error': 'User name already exists'}), 400
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()
        return jsonify({'id': user.id}), 201

    def list_users(self) -> str:
        """
        :return: A json list with the response
        [
          {
            "name" : "<user_name>",
            "display_name" : "<display name>",
            "creation_time" : "<some date:time format>"
          }
        ]
        """
        users = db.session.query(User).all()
        users_schema = UserSchema(many=True)
        users_dict_list = users_schema.dump(users)
        return jsonify(users_dict_list)

    def describe_user(self,request):
        """
          :param request: A json string with the user details
          {
            "id" : "<user_id>"
          }

          :return: A json string with the response

          {
            "name" : "<user_name>",
            "description" : "<some description>",
            "creation_time" : "<some date:time format>"
          }

        """
        data = request.get_json()

        # Extract the "id" field from the request payload
        user_id = data.get("id")
        user = User.query.get(user_id)
        if user is None:
            # Return a 404 Not Found if the user does not exist
            return "User not found", 404

        # Serialize the user to a dictionary
        user_schema = UserSchema(many=False)
        user_dict = user_schema.dump(user)

        # Return the serialized user as a JSON response
        return jsonify(user_dict),200

    def update_user(self, request) -> str:
        """
        :param request: A json string with the user details
        {
          "id" : "<user_id>",
          "user" : {
            "name" : "<user_name>",
            "display_name" : "<display name>"
          }
        }

        :return:

        Constraint:
            * user name cannot be updated
            * name can be max 64 characters
            * display name can be max 128 characters
        """
        update_user_schema=UpdateUserSchema(many=False)
        try:
            data = update_user_schema.load(request.get_json())
        except ValidationError as err:
            return jsonify({'error': err.messages}), 422


        # Extract the user details from the request body
        user_id = data.get("id")
        user = data.get("user")
        user_name = user.get("user_name")
        display_name = user.get("display_name")
        user = User.query.get(user_id)
        if user is None or user.user_name != user_name:
            return jsonify({"error": "Username cannot be updated"}), 400
        user.display_name = display_name
        db.session.commit()
        # Return a success response
        return "User updated successfully", 200

    def list_team_users(self, request):
        """
        :param request: A json string with the team identifier
        {
          "id" : "<team_id>"
        }

        :return:
        [
          {
            "id" : "<user_id>",
            "name" : "<user_name>",
            "display_name" : "<display name>"
          }
        ]
        """
        req_data=request.get_json()
        team_id=req_data.get('id')
        team = Team.query.get(team_id)
        if not team:
            # Return an error if the team does not exist
            return jsonify({'error': 'Team not found'}), 404
        team_user_schema = TeamUserSchema(many=True)
        return team_user_schema.dumps(team.users)
