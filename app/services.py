from flask import Blueprint, render_template, request, jsonify
from app.models import Service, Cart, CartItem, Order, OrderItem, db
from app.payment import get_square_processor
import uuid
from datetime import datetime

services_bp = Blueprint('services', __name__, url_prefix='/services')

# Service categories
CATEGORIES = {
    'industrial_design': 'Industrial Design',
    '3d_printing': '3D Printing',
    'laser_engraving': 'Laser Engraving'
}


@services_bp.route('/')
def catalog():
    """Display all services/products."""
    category = request.args.get('category')
    
    if category and category in CATEGORIES:
        services = Service.query.filter_by(category=category, is_active=True).all()
    else:
        services = Service.query.filter_by(is_active=True).all()
    
    return render_template('services/catalog.html', 
                         services=services,
                         categories=CATEGORIES,
                         selected_category=category)


@services_bp.route('/<slug>')
def service_detail(slug):
    """Display service details."""
    service = Service.query.filter_by(slug=slug).first_or_404()
    return render_template('services/detail.html', service=service)


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
    
    return jsonify({
        'success': True,
        'message': f'{service.name} added to cart',
        'cart_total': cart.get_total(),
        'cart_count': len(cart.items)
    })


@services_bp.route('/cart')
def view_cart():
    """Display shopping cart."""
    session_id = request.cookies.get('cart_session')
    cart = None
    
    if session_id:
        cart = Cart.query.filter_by(session_id=session_id).first()
    
    return render_template('services/cart.html', cart=cart)


@services_bp.route('/checkout')
def checkout():
    """Checkout page."""
    session_id = request.cookies.get('cart_session')
    cart = None
    
    if session_id:
        cart = Cart.query.filter_by(session_id=session_id).first()
    
    if not cart or len(cart.items) == 0:
        return render_template('services/cart_empty.html')
    
    # Pass Square configuration to template
    from flask import current_app
    square_app_id = current_app.config.get('SQUARE_APPLICATION_ID')
    square_location_id = current_app.config.get('SQUARE_LOCATION_ID', '')
    cart_total_cents = int(cart.get_total() * 100)
    
    return render_template('services/checkout.html', 
                         cart=cart,
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
