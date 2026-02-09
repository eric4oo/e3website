"""
Admin Panel - Content Management System
Allows editing of website content, design elements, and settings
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, send_from_directory, current_app
from functools import wraps
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from slugify import slugify
from app import db
from app.models import Service, Category

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Simple password protection (in production, use proper authentication)
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

# Content storage file
CONTENT_FILE = os.path.join(os.path.dirname(__file__), '..', 'instance', 'content.json')

# Media upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'webm', 'mov', 'avi'}

def allowed_file(filename):
    """Check if file is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ensure uploads directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def init_content_file():
    """Initialize content.json with default values if it doesn't exist."""
    if not os.path.exists(CONTENT_FILE):
        default_content = {
            'site_title': 'PropsWorks',
            'site_tagline': 'Custom Props & Low-Volume Manufacturing',
            'hero_title': 'Welcome to PropsWorks',
            'hero_subtitle': 'Professional Props and Manufacturing Services',
            'about_title': 'About PropsWorks',
            'about_content': 'PropsWorks specializes in providing professional manufacturing services for creative professionals, filmmakers, prop makers, and businesses who need high-quality custom-made items.',
            'about_services': 'Industrial Design: Expert design and engineering for your concepts, from sketches to production-ready models\n3D Printing: High-quality 3D printing with various materials and finishing options\nLaser Engraving: Precision laser engraving and cutting for customization and branding',
            'about_why': 'Expert team with years of manufacturing experience\nFast turnaround times and responsive service\nQuality guaranteed on every project\nFlexible for single prototypes to medium volume orders\nCompetitive pricing and custom quotes',
            'about_perfect_for': 'Film and TV production props\nTheater and stage productions\nCustom merchandise and promotional items\nPrototype development and testing\nLimited edition product runs\nPersonalized gifts and awards',
            'about_process': 'Consultation: Discuss your project requirements and vision\nDesign: Create or refine designs for your specifications\nPrototyping: Develop prototypes for approval and testing\nProduction: Manufacture to your exact specifications\nDelivery: Ship finished products to your location',
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
            'instagram_handle': '',
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

# ==================== CATEGORY MANAGEMENT ROUTES ====================

@admin_bp.route('/api/categories')
@login_required
def get_categories():
    """Get all categories with hierarchy."""
    root_categories = Category.query.filter_by(parent_id=None).order_by(Category.order).all()
    return jsonify([cat.to_dict(include_children=True) for cat in root_categories])


@admin_bp.route('/api/categories', methods=['POST'])
@login_required
def create_category():
    """Create a new category."""
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        
        slug = slugify(data['name'])
        
        if Category.query.filter_by(slug=slug).first():
            return jsonify({'success': False, 'error': 'Category with this name already exists'}), 400
        
        category = Category(
            name=data['name'],
            slug=slug,
            parent_id=data.get('parent_id'),
            description=data.get('description', ''),
            order=data.get('order', 0),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Category "{category.name}" created successfully',
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/api/categories/<int:category_id>', methods=['PUT'])
@login_required
def update_category(category_id):
    """Update a category."""
    try:
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        
        if 'name' in data:
            category.name = data['name']
            category.slug = slugify(data['name'])
        if 'parent_id' in data:
            # Prevent a category from being its own parent
            if data['parent_id'] == category_id:
                return jsonify({'success': False, 'error': 'A category cannot be its own parent'}), 400
            category.parent_id = data['parent_id']
        if 'description' in data:
            category.description = data['description']
        if 'order' in data:
            category.order = data['order']
        if 'is_active' in data:
            category.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Category "{category.name}" updated successfully',
            'category': category.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/api/categories/<int:category_id>', methods=['DELETE'])
@login_required
def delete_category(category_id):
    """Delete a category."""
    try:
        category = Category.query.get_or_404(category_id)
        
        # Check if category has items
        if category.services:
            return jsonify({
                'success': False,
                'error': f'Cannot delete category with {len(category.services)} item(s). Please reassign items first.'
            }), 400
        
        # Check if category has sub-categories
        if category.children:
            return jsonify({
                'success': False,
                'error': f'Cannot delete category with {len(category.children)} sub-category(ies). Please delete sub-categories first.'
            }), 400
        
        category_name = category.name
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Category "{category_name}" deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/items')
@login_required
def manage_items():
    """Item management page."""
    categories = Category.query.filter_by(parent_id=None).order_by(Category.order).all()
    return render_template('admin/items.html', categories=[cat.to_dict(include_children=True) for cat in categories])

@admin_bp.route('/categories')
@login_required
def manage_categories():
    """Category management page."""
    return render_template('admin/categories.html')


@admin_bp.route('/about')
@login_required
def edit_about():
    """Edit about page content."""
    content = load_content()
    return render_template('admin/about.html', content=content)


@admin_bp.route('/api/content/about', methods=['PUT'])
@login_required
def update_about_content():
    """Update about page content."""
    try:
        content = load_content()
        data = request.get_json()
        
        # Update about content fields
        if 'about_title' in data:
            content['about_title'] = data['about_title']
        if 'about_content' in data:
            content['about_content'] = data['about_content']
        if 'about_description' in data:
            content['about_description'] = data['about_description']
        if 'about_services' in data:
            content['about_services'] = data['about_services']
        if 'about_why' in data:
            content['about_why'] = data['about_why']
        if 'about_perfect_for' in data:
            content['about_perfect_for'] = data['about_perfect_for']
        if 'about_process' in data:
            content['about_process'] = data['about_process']
        if 'contact_email' in data:
            content['contact_email'] = data['contact_email']
        if 'instagram_handle' in data:
            content['instagram_handle'] = data['instagram_handle']
        
        save_content(content)
        return jsonify({'success': True, 'message': 'About page content updated successfully'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/contact')
@login_required
def edit_contact():
    """Edit contact page content."""
    content = load_content()
    return render_template('admin/contact.html', content=content)


@admin_bp.route('/api/content/contact', methods=['PUT'])
@login_required
def update_contact_content():
    """Update contact page content."""
    try:
        content = load_content()
        data = request.get_json()
        
        # Update contact content fields
        if 'contact_title' in data:
            content['contact_title'] = data['contact_title']
        if 'contact_intro' in data:
            content['contact_intro'] = data['contact_intro']
        if 'contact_message' in data:
            content['contact_message'] = data['contact_message']
        if 'contact_email' in data:
            content['contact_email'] = data['contact_email']
        if 'instagram_handle' in data:
            content['instagram_handle'] = data['instagram_handle']
        
        save_content(content)
        return jsonify({'success': True, 'message': 'Contact page content updated successfully'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/api/items')
@login_required
def get_items():
    """Get all items with optional category filter."""
    category_id = request.args.get('category_id')
    query = Service.query
    
    if category_id:
        try:
            category_id = int(category_id)
            query = query.filter_by(category_id=category_id)
        except (ValueError, TypeError):
            pass
    
    items = query.all()
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'price_base': item.price_base,
        'category_id': item.category_id,
        'sub_category_id': item.sub_category_id,
        'category_name': item.category_obj.name if item.category_obj else None,
        'sub_category_name': item.sub_category_obj.name if item.sub_category_obj else None,
        'image_url': item.image_url,
        'is_active': item.is_active,
        'media_gallery': item.media_gallery or [],
        'bulk_pricing': item.bulk_pricing or [],
        'variants': item.variants or [],
        'created_at': item.created_at.isoformat()
    } for item in items])



@admin_bp.route('/api/items/<int:item_id>')
@login_required
def get_item(item_id):
    """Get specific item details."""
    item = Service.query.get_or_404(item_id)
    return jsonify({
        'id': item.id,
        'name': item.name,
        'slug': item.slug,
        'description': item.description,
        'long_description': item.long_description,
        'price_base': item.price_base,
        'category_id': item.category_id,
        'sub_category_id': item.sub_category_id,
        'category_name': item.category_obj.name if item.category_obj else None,
        'sub_category_name': item.sub_category_obj.name if item.sub_category_obj else None,
        'image_url': item.image_url,
        'is_active': item.is_active,
        'media_gallery': item.media_gallery or [],
        'bulk_pricing': item.bulk_pricing or [],
        'variants': item.variants or [],
        'created_at': item.created_at.isoformat()
    })



@admin_bp.route('/api/items', methods=['POST'])
@login_required
def create_item():
    """Create a new item/service."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name') or not data.get('category_id'):
            return jsonify({'success': False, 'error': 'Name and category are required'}), 400
        
        # Create slug from name
        slug = slugify(data['name'])
        
        # Check if slug already exists
        if Service.query.filter_by(slug=slug).first():
            return jsonify({'success': False, 'error': 'Item with this name already exists'}), 400
        
        # Handle optional price (None = Contact for Quote)
        price_base = data.get('price_base')
        if price_base == '' or price_base is None:
            price_base = None
        else:
            price_base = float(price_base)
        
        item = Service(
            name=data['name'],
            slug=slug,
            description=data.get('description', ''),
            long_description=data.get('long_description', ''),
            price_base=price_base,
            category_id=int(data['category_id']),
            sub_category_id=int(data['sub_category_id']) if data.get('sub_category_id') else None,
            image_url=data.get('image_url', ''),
            is_active=data.get('is_active', True),
            media_gallery=data.get('media_gallery', []),
            bulk_pricing=data.get('bulk_pricing', []),
            variants=data.get('variants', [])
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Item "{item.name}" created successfully',
            'item_id': item.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/api/items/<int:item_id>', methods=['PUT'])
@login_required
def update_item(item_id):
    """Update an existing item."""
    try:
        item = Service.query.get_or_404(item_id)
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            item.name = data['name']
        if 'description' in data:
            item.description = data['description']
        if 'long_description' in data:
            item.long_description = data['long_description']
        if 'price_base' in data:
            price_base = data['price_base']
            if price_base == '' or price_base is None:
                item.price_base = None
            else:
                item.price_base = float(price_base)
        if 'category_id' in data:
            item.category_id = int(data['category_id'])
        if 'sub_category_id' in data:
            item.sub_category_id = int(data['sub_category_id']) if data['sub_category_id'] else None
        if 'image_url' in data:
            item.image_url = data['image_url']
        if 'is_active' in data:
            item.is_active = data['is_active']
        if 'media_gallery' in data:
            item.media_gallery = data['media_gallery']
        if 'bulk_pricing' in data:
            item.bulk_pricing = data['bulk_pricing']
        if 'variants' in data:
            item.variants = data['variants']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Item "{item.name}" updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/api/items/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    """Delete an item."""
    try:
        item = Service.query.get_or_404(item_id)
        item_name = item.name
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Item "{item_name}" deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/api/items/<int:item_id>/upload-media', methods=['POST'])
@login_required
def upload_media(item_id):
    """Upload media (photo/video) for an item."""
    try:
        item = Service.query.get_or_404(item_id)
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        caption = request.form.get('caption', '')
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'File type not allowed'}), 400
        
        # Save file with secure filename
        filename = secure_filename(f"{item_id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Determine media type
        ext = filename.rsplit('.', 1)[1].lower()
        media_type = 'video' if ext in {'mp4', 'webm', 'mov', 'avi'} else 'photo'
        
        # Add to media gallery
        media_url = f'/static/uploads/{filename}'
        media_item = {
            'type': media_type,
            'url': media_url,
            'caption': caption,
            'uploaded_at': datetime.utcnow().isoformat()
        }
        
        if not item.media_gallery:
            item.media_gallery = []
        
        item.media_gallery.append(media_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Media uploaded successfully',
            'media': media_item
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/api/items/<int:item_id>/media/<int:media_index>', methods=['DELETE'])
@login_required
def delete_media(item_id, media_index):
    """Delete media from an item."""
    try:
        item = Service.query.get_or_404(item_id)
        
        if not item.media_gallery or media_index >= len(item.media_gallery):
            return jsonify({'success': False, 'error': 'Media not found'}), 404
        
        media = item.media_gallery[media_index]
        
        # Delete file from disk
        filename = media['url'].split('/')[-1]
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Remove from gallery
        item.media_gallery.pop(media_index)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Media deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400