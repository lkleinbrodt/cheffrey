import os
from dotenv import load_dotenv
load_dotenv()


class Config:
    ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY') 
    ENV = os.environ.get('ENV', 'dev').lower()
    assert ENV in ['dev', 'prod', 'test']
    if SECRET_KEY is None:
        raise ValueError("No SECRET_KEY set for Flask application")
    
    if ENV == 'dev':
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(ROOT_DIR, 'app.db')
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://')
    
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    S3_BUCKET = os.environ.get('S3_BUCKET')