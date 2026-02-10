from flask import Blueprint, render_template, request, jsonify, make_response
from app.models import Service, Cart, CartItem, Order, OrderItem, Category, db
from app.payment import get_square_processor
from app.shipping import CanadaPostShippingService
import uuid
from datetime import datetime
import json
import os

services_bp = Blueprint('services', __name__, url_prefix='/services')

def load_categories():
    """Load categories from database."""
    try:
        root_categories = Category.query.filter_by(parent_id=None, is_active=True).order_by(Category.order).all()
        categories = {}
        for cat in root_categories:
            categories[cat.id] = {
                'id': cat.id,
                'name': cat.name,
                'slug': cat.slug,
                'children': {}
            }
            if cat.children:
                for subcat in sorted(cat.children, key=lambda x: x.order):
                    if subcat.is_active:
                        categories[cat.id]['children'][subcat.id] = {
                            'id': subcat.id,
                            'name': subcat.name,
                            'slug': subcat.slug
                        }
        return categories
    except Exception:
        # Fallback if database is not initialized
        return {}

def load_content():
    """Load content from JSON file."""
    content_file = os.path.join(os.path.dirname(__file__), '..', 'instance', 'content.json')
    if os.path.exists(content_file):
        with open(content_file, 'r') as f:
            return json.load(f)
    return {}


@services_bp.route('/')
def catalog():
    """Display all services/products."""
    category_param = request.args.get('category')
    subcategory_param = request.args.get('subcategory')
    content = load_content()
    categories = load_categories()
    
    selected_category = None
    selected_subcategory = None
    parent_category = None
    
    if subcategory_param:
        # Filtering by subcategory
        subcategory = Category.query.filter_by(slug=subcategory_param, is_active=True).first()
        if subcategory:
            services = Service.query.filter_by(category_id=subcategory.id, is_active=True).all()
            selected_subcategory = subcategory_param
            parent_category = subcategory.parent
            selected_category = parent_category.slug if parent_category else None
        else:
            services = Service.query.filter_by(is_active=True).all()
    elif category_param:
        # Find category by slug
        category = Category.query.filter_by(slug=category_param, parent_id=None, is_active=True).first()
        if category:
            services = Service.query.filter_by(category_id=category.id, is_active=True).all()
            selected_category = category_param
            parent_category = category
        else:
            services = Service.query.filter_by(is_active=True).all()
    else:
        services = Service.query.filter_by(is_active=True).all()
    
    return render_template('services/catalog.html', 
                         services=services,
                         categories=categories,
                         selected_category=selected_category,
                         selected_subcategory=selected_subcategory,
                         parent_category=parent_category,
                         content=content)


@services_bp.route('/<slug>')
def service_detail(slug):
    """Display service details."""
    content = load_content()
    service = Service.query.filter_by(slug=slug).first_or_404()
    return render_template('services/detail.html', service=service, content=content)


@services_bp.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    """Add service to cart."""
    data = request.get_json()
    service_id = data.get('service_id')
    quantity = data.get('quantity', 1)
    options = data.get('options', {})
    
    service = Service.query.get_or_404(service_id)
    
    # Get or create cart (using session ID)
    session_id = request.cookies.get('cart_session')
    if not session_id:
        session_id = uuid.uuid4().hex
    
    cart = Cart.query.filter_by(session_id=session_id).first()
    if not cart:
        cart = Cart(session_id=session_id)
        db.session.add(cart)
        db.session.commit()
    
    # Calculate price
    price = service.price_base
    for option_key, option_value in options.items():
        # Add logic to adjust price based on selected options
        pass
    
    # Add item to cart
    cart_item = CartItem(
        cart_id=cart.id,
        service_id=service_id,
        quantity=quantity,
        custom_options=options,
        price_at_time=price
    )
    db.session.add(cart_item)
    db.session.commit()
    
    response_data = {
        'success': True,
        'message': f'{service.name} added to cart',
        'cart_total': cart.get_total(),
        'cart_count': len(cart.items)
    }
    
    # Create response with cookie
    response = make_response(jsonify(response_data))
    response.set_cookie('cart_session', session_id, max_age=2592000, secure=False, httponly=False, samesite='Lax')
    return response


@services_bp.route('/cart')
def view_cart():
    """Display shopping cart."""
    content = load_content()
    session_id = request.cookies.get('cart_session')
    cart = None
    
    if session_id:
        cart = Cart.query.filter_by(session_id=session_id).first()
    
    return render_template('services/cart.html', cart=cart, content=content)


@services_bp.route('/cart-count', methods=['GET'])
def get_cart_count():
    """Get the current cart item count."""
    session_id = request.cookies.get('cart_session')
    cart_count = 0
    
    if session_id:
        cart = Cart.query.filter_by(session_id=session_id).first()
        if cart:
            cart_count = len(cart.items)
    
    return jsonify({
        'cart_count': cart_count
    })


@services_bp.route('/api/shipping-rates', methods=['POST'])
def get_shipping_rates():
    """
    Get real-time shipping rates based on destination postal code and cart weight.
    
    Request JSON:
    {
        'destination_postal_code': 'N9J 1V6',
        'domestic_only': True
    }
    """
    try:
        data = request.get_json()
        destination_postal_code = data.get('destination_postal_code', '').strip()
        domestic_only = data.get('domestic_only', True)
        
        # Get cart items to calculate weight
        session_id = request.cookies.get('cart_session')
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Cart not found'
            }), 400
        
        cart = Cart.query.filter_by(session_id=session_id).first()
        if not cart or len(cart.items) == 0:
            return jsonify({
                'success': False,
                'error': 'Cart is empty'
            }), 400
        
        # Calculate total weight from cart items
        cart_items_data = [
            {
                'weight_kg': item.service.weight_kg,
                'quantity': item.quantity
            }
            for item in cart.items
        ]
        total_weight = CanadaPostShippingService.calculate_total_weight(cart_items_data)
        
        # Get shipping rates (try real API first, fallback to demo)
        rates = CanadaPostShippingService.get_shipping_rates(
            destination_postal_code,
            total_weight,
            domestic_only
        )
        
        # If no API credentials, use demo rates
        if not rates['success'] and 'credentials not configured' in (rates.get('error') or ''):
            rates = CanadaPostShippingService.get_demo_shipping_rates(
                destination_postal_code,
                total_weight
            )
            rates['is_demo'] = True
        
        return jsonify(rates)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error calculating shipping: {str(e)}'
        }), 500


@services_bp.route('/checkout')
def checkout():
    """Checkout page."""
    content = load_content()
    session_id = request.cookies.get('cart_session')
    cart = None
    
    if session_id:
        cart = Cart.query.filter_by(session_id=session_id).first()
    
    if not cart or len(cart.items) == 0:
        return render_template('services/cart_empty.html', content=content)
    
    # Pass Square configuration to template
    from flask import current_app
    square_app_id = current_app.config.get('SQUARE_APPLICATION_ID')
    square_location_id = current_app.config.get('SQUARE_LOCATION_ID', '')
    cart_total_cents = int(cart.get_total() * 100)
    
    return render_template('services/checkout.html', 
                         cart=cart,
                         content=content,
                         square_app_id=square_app_id,
                         square_location_id=square_location_id,
                         cart_total_cents=cart_total_cents)


@services_bp.route('/process-payment', methods=['POST'])
def process_payment():
    """Process payment through Square."""
    try:
        data = request.get_json()
        
        # Get cart
        session_id = request.cookies.get('cart_session')
        if not session_id:
            return jsonify({'success': False, 'error': 'Cart not found'}), 400
        
        cart = Cart.query.filter_by(session_id=session_id).first()
        if not cart or len(cart.items) == 0:
            return jsonify({'success': False, 'error': 'Cart is empty'}), 400
        
        # Extract customer information
        customer_name = data.get('customer_name')
        customer_email = data.get('customer_email')
        customer_phone = data.get('customer_phone')
        customer_address = data.get('customer_address')
        customer_city = data.get('customer_city')
        customer_state = data.get('customer_state')
        customer_zip = data.get('customer_zip')
        nonce = data.get('nonce')
        amount_cents = data.get('amount')
        
        # Extract shipping information
        shipping_method = data.get('shipping_method', 'DOM.RP')
        shipping_service_name = data.get('shipping_service_name', 'Regular Parcel')
        shipping_cost = float(data.get('shipping_cost', 0))
        
        # Process payment with Square
        processor = get_square_processor()
        payment_result = processor.process_payment(
            amount_cents=amount_cents,
            source_id=nonce
        )
        
        if not payment_result['success']:
            return jsonify({
                'success': False,
                'error': payment_result.get('error', 'Payment failed')
            }), 400
        
        # Calculate subtotal (amount without shipping)
        cart_subtotal = cart.get_total()
        
        # Create order in database
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        order = Order(
            order_number=order_number,
            customer_email=customer_email,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_address=customer_address,
            customer_city=customer_city,
            customer_state=customer_state,
            customer_zip=customer_zip,
            shipping_method=shipping_method,
            shipping_service_name=shipping_service_name,
            shipping_cost=shipping_cost,
            subtotal=cart_subtotal,
            total_amount=amount_cents / 100,
            status='processing',
            payment_status='paid',
            square_payment_id=payment_result['payment_id']
        )
        db.session.add(order)
        db.session.flush()
        
        # Add order items from cart
        for cart_item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                service_id=cart_item.service_id,
                service_name=cart_item.service.name,
                quantity=cart_item.quantity,
                unit_price=cart_item.price_at_time,
                custom_options=cart_item.custom_options
            )
            db.session.add(order_item)
        
        # Clear cart
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.delete(cart)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'order_id': order.id,
            'order_number': order_number,
            'message': 'Payment successful!'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error processing payment: {str(e)}'
        }), 500


@services_bp.route('/order-confirmation')
def order_confirmation():
    """Display order confirmation."""
    order_id = request.args.get('order_id')
    
    if not order_id:
        return render_template('services/cart_empty.html')
    
    order = Order.query.get_or_404(order_id)
    return render_template('services/order_confirmation.html', order=order)
