from datetime import datetime

from sqlalchemy import Integer, Enum, UniqueConstraint

from database.database import db


class UserTeam(db.Model):
    __tablename__ = 'user_team'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), primary_key=True)



class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(64), unique=True)
    display_name = db.Column(db.String(64))
    creation_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    teams = db.relationship('Team', secondary='user_team', backref=db.backref('users', lazy='dynamic'))


class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=True)
    admin = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creation_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)


status_enum = Enum('OPEN', 'CLOSED', name='status_enum')

class Board(db.Model):
    __tablename__ = 'board'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(128))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    creation_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    status = db.Column(status_enum, default='OPEN')
    tasks = db.relationship('Task', backref='board', lazy=True)
    __table_args__ = (
        db.UniqueConstraint('name', 'team_id', name='unique_board_name_for_team'),
    )

task_status_enum = Enum('OPEN', 'IN_PROGRESS', 'COMPLETE', name='task_status_enum')
class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.String(64))
    creation_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    status = db.Column(task_status_enum, default='OPEN')
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'), nullable=False)
    __table_args__ = (
        UniqueConstraint('title', 'board_id', name='unique_task_title_for_board'),
    )
