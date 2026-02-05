from datetime import datetime
from app import db

class Category(db.Model):
    """Product/Service categories with parent-child hierarchy."""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)  # None for root categories
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)  # For sorting
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Self-referential relationship for parent/child
    children = db.relationship('Category', 
                              backref=db.backref('parent', remote_side=[id]),
                              cascade='all, delete-orphan')
    
    # Relationship to services in this category (as parent category)
    services = db.relationship('Service', 
                              foreign_keys='Service.category_id',
                              backref='category_obj', 
                              lazy=True)
    
    # Relationship to services in this category (as sub-category)
    sub_services = db.relationship('Service', 
                                  foreign_keys='Service.sub_category_id',
                                  backref='sub_category_obj')
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self, include_children=False):
        """Convert category to dictionary."""
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'parent_id': self.parent_id,
            'description': self.description,
            'order': self.order,
            'is_active': self.is_active
        }
        if include_children and self.children:
            data['children'] = [child.to_dict(include_children=True) for child in sorted(self.children, key=lambda x: x.order)]
        return data


class Service(db.Model):
    """Service/Product model for e-commerce."""
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    long_description = db.Column(db.Text)
    price_base = db.Column(db.Float, nullable=True)  # None = Contact for Quote
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)  # Parent category (e.g., Industrial Design)
    sub_category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)  # Optional sub-category (e.g., CAD)
    image_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    media_gallery = db.Column(db.JSON, default=list)  # Stores list of media: [{'type': 'photo/video', 'url': '...', 'caption': '...'}]
    bulk_pricing = db.Column(db.JSON, default=list)  # Stores bulk pricing tiers: [{'min_quantity': 10, 'price': 450}]
    variants = db.Column(db.JSON, default=list)  # Stores product variants: [{'name': 'Small', 'price': 100, 'description': '...', 'sku': '...', 'is_available': True}]
    
    # Relationships
    service_options = db.relationship('ServiceOption', backref='service', lazy=True, cascade='all, delete-orphan')

    
    def __repr__(self):
        return f'<Service {self.name}>'
    
    def requires_quote(self):
        """Check if this item requires a quote (no base price set)."""
        return self.price_base is None
    
    def get_price_for_quantity(self, quantity):
        """Get price based on quantity, considering bulk discounts. Returns None if quote required."""
        if self.price_base is None:
            return None
            
        if not self.bulk_pricing:
            return self.price_base
        
        applicable_tier = None
        for tier in sorted(self.bulk_pricing, key=lambda x: x['min_quantity'], reverse=True):
            if quantity >= tier['min_quantity']:
                applicable_tier = tier
                break
        
        return applicable_tier['price'] if applicable_tier else self.price_base


class ServiceOption(db.Model):
    """Options/variations for services (e.g., material types, sizes)."""
    __tablename__ = 'service_options'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    option_name = db.Column(db.String(255), nullable=False)
    option_type = db.Column(db.String(100), nullable=False)  # material, size, finish, etc.
    price_adjustment = db.Column(db.Float, default=0)
    is_available = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<ServiceOption {self.option_name}>'


class Cart(db.Model):
    """Shopping cart for users."""
    __tablename__ = 'carts'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')
    
    def get_total(self):
        return sum(item.get_subtotal() for item in self.items)


class CartItem(db.Model):
    """Individual items in shopping cart."""
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    custom_options = db.Column(db.JSON)  # Store selected options as JSON
    price_at_time = db.Column(db.Float, nullable=False)
    
    # Relationships
    service = db.relationship('Service', backref='cart_items')
    
    def get_subtotal(self):
        return self.price_at_time * self.quantity


class Order(db.Model):
    """Customer orders."""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_email = db.Column(db.String(255), nullable=False)
    customer_name = db.Column(db.String(255), nullable=False)
    customer_phone = db.Column(db.String(20))
    customer_address = db.Column(db.String(255))
    customer_city = db.Column(db.String(100))
    customer_state = db.Column(db.String(50))
    customer_zip = db.Column(db.String(10))
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, cancelled
    payment_status = db.Column(db.String(50), default='unpaid')  # unpaid, paid, failed
    square_payment_id = db.Column(db.String(255))
    square_order_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.order_number}>'


class OrderItem(db.Model):
    """Individual items in an order."""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    service_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    custom_options = db.Column(db.JSON)
    
    # Relationships
    service = db.relationship('Service', backref='order_items')
    
    def get_subtotal(self):
        return self.unit_price * self.quantity
