from flasgger import Swagger
from flask import Flask
from api.board_api import board_bp
from api.bueprint_api import team_bp, swaggerui_blueprint

from api.user_api import user_bp

from database.database import db


swagger=None
app = Flask(__name__)
def create_app():

    # configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.database'
    db.init_app(app)
    app.register_blueprint(user_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(board_bp)
    app.config['SWAGGER'] = {
        "swagger_version": "2.0",
        "title": "My API",
        "description": "API for managing users",
    }

    global swagger

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    return app

def setup_database(app):
    with app.app_context():
        db.create_all()

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'





if __name__ == '__main__':
    app = create_app()
    app.run()
    setup_database(app)

