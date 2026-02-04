from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page route."""
    return render_template('index.html', title='Home')

@main_bp.route('/about')
def about():
    """About page route."""
    return render_template('about.html', title='About')

@main_bp.route('/health')
def health():
    """Health check endpoint for deployment monitoring."""
    return {'status': 'healthy'}, 200
