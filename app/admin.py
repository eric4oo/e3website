"""
Admin Panel - Content Management System
Allows editing of website content, design elements, and settings
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import json
import os
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Simple password protection (in production, use proper authentication)
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

# Content storage file
CONTENT_FILE = os.path.join(os.path.dirname(__file__), '..', 'instance', 'content.json')


def init_content_file():
    """Initialize content.json with default values if it doesn't exist."""
    if not os.path.exists(CONTENT_FILE):
        default_content = {
            'site_title': 'PropsWorks',
            'site_tagline': 'Custom Props & Low-Volume Manufacturing',
            'hero_title': 'Welcome to PropsWorks',
            'hero_subtitle': 'Professional Props and Manufacturing Services',
            'about_title': 'About PropsWorks',
            'about_content': 'We specialize in creating custom props and providing low-volume manufacturing services.',
            'services': {
                'industrial_design': {
                    'title': 'Industrial Design',
                    'description': 'Custom industrial design services',
                    'price': 5000
                },
                '3d_printing': {
                    'title': '3D Printing',
                    'description': 'High-quality 3D printing services',
                    'price': 1000
                },
                'laser_engraving': {
                    'title': 'Laser Engraving',
                    'description': 'Precision laser engraving services',
                    'price': 500
                }
            },
            'colors': {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'accent': '#e74c3c',
                'background': '#ecf0f1',
                'text': '#2c3e50'
            },
            'contact_email': 'info@propsworks.com',
            'contact_phone': '(555) 123-4567',
            'last_updated': datetime.now().isoformat()
        }
        os.makedirs(os.path.dirname(CONTENT_FILE), exist_ok=True)
        with open(CONTENT_FILE, 'w') as f:
            json.dump(default_content, f, indent=2)


def load_content():
    """Load content from JSON file."""
    init_content_file()
    with open(CONTENT_FILE, 'r') as f:
        return json.load(f)


def save_content(content):
    """Save content to JSON file."""
    content['last_updated'] = datetime.now().isoformat()
    with open(CONTENT_FILE, 'w') as f:
        json.dump(content, f, indent=2)


def login_required(f):
    """Decorator to require admin login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            return render_template('admin/login.html', error='Invalid password'), 401
    return render_template('admin/login.html')


@admin_bp.route('/logout')
def logout():
    """Logout from admin panel."""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard - main content editor."""
    content = load_content()
    return render_template('admin/dashboard.html', content=content)


@admin_bp.route('/api/content', methods=['GET'])
@login_required
def get_content():
    """API endpoint to get all content."""
    return jsonify(load_content())


@admin_bp.route('/api/content', methods=['POST'])
@login_required
def save_all_content():
    """API endpoint to save all content."""
    try:
        content = request.get_json()
        save_content(content)
        return jsonify({'success': True, 'message': 'Content saved successfully'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/api/content/<key>', methods=['PUT'])
@login_required
def update_content_item(key):
    """API endpoint to update a specific content item."""
    try:
        content = load_content()
        data = request.get_json()
        
        # Handle nested keys (e.g., 'colors.primary')
        if '.' in key:
            keys = key.split('.')
            target = content
            for k in keys[:-1]:
                if k not in target:
                    target[k] = {}
                target = target[k]
            target[keys[-1]] = data['value']
        else:
            content[key] = data['value']
        
        save_content(content)
        return jsonify({'success': True, 'message': f'{key} updated successfully'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/api/content/service/<service_id>', methods=['PUT'])
@login_required
def update_service(service_id):
    """API endpoint to update service details."""
    try:
        content = load_content()
        data = request.get_json()
        
        if service_id in content['services']:
            content['services'][service_id].update(data)
            save_content(content)
            return jsonify({'success': True, 'message': f'Service {service_id} updated'}), 200
        else:
            return jsonify({'success': False, 'error': 'Service not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/api/preview')
@login_required
def get_preview_data():
    """Get content data for live preview."""
    return jsonify(load_content())
