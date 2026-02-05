from flask import Blueprint, render_template
import json
import os

main_bp = Blueprint('main', __name__)

def load_content():
    """Load content from JSON file."""
    content_file = os.path.join(os.path.dirname(__file__), '..', 'instance', 'content.json')
    if os.path.exists(content_file):
        with open(content_file, 'r') as f:
            return json.load(f)
    return {}

@main_bp.route('/')
def index():
    """Home page route."""
    content = load_content()
    return render_template('index.html', title='Home', content=content)

@main_bp.route('/about')
def about():
    """About page route."""
    content = load_content()
    return render_template('about.html', title='About', content=content)

@main_bp.route('/health')
def health():
    """Health check endpoint for deployment monitoring."""
    return {'status': 'healthy'}, 200
