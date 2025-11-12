import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Roopa%40531984@localhost/employee_tracker_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
