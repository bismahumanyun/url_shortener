# config.py
import os


class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:pwd@localhost/url_shortener'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-secret-key'
