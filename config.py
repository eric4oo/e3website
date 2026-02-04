import os
from datetime import timedelta

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Square Payment
    SQUARE_APPLICATION_ID = os.environ.get('SQUARE_APPLICATION_ID')
    SQUARE_ACCESS_TOKEN = os.environ.get('SQUARE_ACCESS_TOKEN')
    SQUARE_ENVIRONMENT = os.environ.get('SQUARE_ENVIRONMENT', 'production')
    SQUARE_LOCATION_ID = os.environ.get('SQUARE_LOCATION_ID', '')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///ecommerce.db')

class ProductionConfig(Config):
    """Production configuration for DigitalOcean."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///ecommerce.db')
