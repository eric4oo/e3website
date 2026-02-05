import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_name='development'):
    """Application factory function."""
    # Get the root directory (parent of the app module)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Create Flask app with correct template and static paths
    app = Flask(__name__, 
                template_folder=os.path.join(root_dir, 'templates'),
                static_folder=os.path.join(root_dir, 'static'))
    
    # Load configuration
    if config_name == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    from app.routes import main_bp
    from app.services import services_bp
    from app.admin import admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(admin_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
