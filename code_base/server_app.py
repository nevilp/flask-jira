from flask import Flask


from api.board_api import board_bp
from api.team_api import team_bp
from api.user_api import user_bp
from database.database import db


def create_app():
    app = Flask(__name__)
    # configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.database'
    db.init_app(app)
    app.register_blueprint(user_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(board_bp)
    return app

def setup_database(app):
    with app.app_context():
        db.create_all()




if __name__ == '__main__':
    app = create_app()
    app.run()
    setup_database(app)
