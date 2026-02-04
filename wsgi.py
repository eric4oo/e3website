"""
WSGI entry point for production deployment on DigitalOcean.
Compatible with Gunicorn and other WSGI servers.
"""
import os
from app import create_app

# Set environment
env = os.environ.get('FLASK_ENV', 'production')
app = create_app(config_name=env)

if __name__ == '__main__':
    app.run()
