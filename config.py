import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__) )
load_dotenv()

class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False