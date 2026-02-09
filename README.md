# PropsWorks - Custom Manufacturing E-Commerce Platform

A professional e-commerce platform for specialized manufacturing services including Industrial Design, 3D Printing, and Laser Engraving. Perfect for props, custom projects, and low to medium volume orders.

## 🚀 Features

**E-Commerce Capabilities:**
- Service catalog with categories (Industrial Design, 3D Printing, Laser Engraving)
- Shopping cart functionality with session-based tracking
- Product detail pages with options and customizations
- Order management system with tracking
- Customer information collection
- Integration-ready for Stripe payment processing

**Backend Services:**
- Flask 3.0 framework with application factory pattern
- SQLAlchemy ORM for database management
- Flexible service options and pricing system
- Order tracking and management
- Cart persistence across sessions

**Frontend Features:**
- Responsive design optimized for mobile and desktop
- Service browsing and filtering by category
- Shopping cart visualization
- Checkout process
- Professional styling and UI/UX

**Deployment Ready:**
- Docker & Docker Compose for containerization
- Production-ready Gunicorn WSGI server
- Health check endpoints for monitoring
- Environment-based configuration
- Optimized for DigitalOcean deployment

## 📋 Project Structure

```
website/
├── app/
│   ├── __init__.py          # Flask app factory with database setup
│   ├── models.py            # Database models (Service, Cart, Order, etc.)
│   ├── routes.py            # Main site routes
│   └── services.py          # E-commerce service routes
├── static/
│   ├── css/
│   │   └── style.css        # Comprehensive e-commerce styling
│   └── js/
│       └── script.js        # Cart and e-commerce functionality
├── templates/
│   ├── base.html            # Base template with navbar and footer
│   ├── index.html           # Home page with service showcase
│   ├── about.html           # About page with company info
│   └── services/
│       ├── catalog.html     # Services listing and filtering
│       ├── detail.html      # Individual service details
│       ├── cart.html        # Shopping cart view
│       ├── checkout.html    # Checkout page
│       └── cart_empty.html  # Empty cart message
├── config.py                # Development/Production configuration
├── wsgi.py                  # WSGI entry point for production
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose setup
├── .env.example             # Example environment variables
├── .env                     # Local environment variables
└── README.md               # This file
```

## 💾 Database Models

### Service
- Service catalog entries with pricing and descriptions
- Relationships with ServiceOptions and CartItems

### ServiceOption
- Customizable options for services (materials, sizes, finishes)
- Price adjustments based on selected options

### Cart & CartItem
- Session-based shopping cart
- Cart items with quantity and custom options

### Order & OrderItem
- Complete order history and tracking
- Payment status management
- Integration with Stripe payment IDs

## 🛠️ Requirements

- Python 3.11+
- pip package manager
- Docker & Docker Compose (optional, for containerized deployment)
- SQLite (default, included)

## 📦 Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd website

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment
cp .env.example .env

# Edit .env with your settings
# Important settings:
# - SECRET_KEY: Generate a secure key
# - STRIPE_PUBLIC_KEY: Add your Stripe public key
# - STRIPE_SECRET_KEY: Add your Stripe secret key
```

### 3. Initialize Database

```bash
# Database is created automatically on first run
# Tables will be created when the app starts
```

## 🚀 Running Locally

### Development Server

```bash
# Start Flask development server
python -m flask run

# Visit http://localhost:5000
```

### Docker Compose

```bash
# Build and run containers
docker-compose up

# Visit http://localhost:8000
```

### Admin Panel (Content Management)

Access the interactive admin panel to edit all website content without code:

```bash
# After starting the server, visit:
http://localhost:5000/admin/login

# Default password: admin123
# (Change in .env: ADMIN_PASSWORD=your_password)
```

**Admin Panel Features:**
- Edit site title, tagline, and taglines
- Manage service descriptions and prices
- Customize color scheme
- Update contact information
- Live preview of changes
- All changes auto-saved to JSON

For detailed admin panel documentation, see [ADMIN_PANEL.md](./ADMIN_PANEL.md)

## 📖 Usage

### Adding Services to Catalog

The database will be created automatically. You can add services through:
1. Python shell or management interface
2. Direct database insertion
3. Future admin panel (to be added)

### Shopping Cart

- Users can browse services by category
- Add items to cart from any service page
- View and manage cart items
- Proceed to checkout
- Cart is session-based (persists across page navigations)

### Checkout Process

1. Add items to cart
2. Review cart items
3. Enter shipping information
4. Proceed to payment (Stripe integration ready)
5. Order confirmation

## 💳 Stripe Payment Integration

### Setup Instructions

1. Create Stripe account at https://stripe.com
2. Get API keys from Stripe dashboard
3. Add to `.env`:
   ```
   STRIPE_PUBLIC_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   ```

### Implementation Status

- Checkout form ready
- Payment processing (ready for implementation)
- Order creation on successful payment (ready for implementation)

## ☁️ DigitalOcean Deployment

### Option 1: App Platform (Recommended)

1. **Connect Repository**
   - Go to DigitalOcean > App Platform
   - Connect your GitHub repository

2. **Configure App**
   - Select "Dockerfile" as source
   - Set environment variables:
     - `FLASK_ENV`: `production`
     - `SECRET_KEY`: Generate secure key
     - `STRIPE_PUBLIC_KEY`: Your Stripe public key
     - `STRIPE_SECRET_KEY`: Your Stripe secret key
     - `DATABASE_URL`: PostgreSQL connection string (recommended for production)

3. **Deploy**
   - Click "Deploy"
   - Monitor deployment logs

### Option 2: Droplet

1. **Create Droplet**
   ```bash
   # SSH into droplet
   ssh root@your_droplet_ip
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```

2. **Deploy Application**
   ```bash
   git clone <repository-url>
   cd website
   docker build -t propsworks:latest .
   docker run -d -p 80:8000 \
     -e FLASK_ENV=production \
     -e SECRET_KEY=your-secure-key \
     -e STRIPE_PUBLIC_KEY=your_key \
     -e STRIPE_SECRET_KEY=your_key \
     --restart always \
     propsworks:latest
   ```

3. **Setup Reverse Proxy (Nginx)**
   ```bash
   apt-get update
   apt-get install -y nginx
   
   # Configure nginx to proxy to port 8000
   # Edit /etc/nginx/sites-available/default
   ```

## 🗄️ Database Configuration

### Development (SQLite)
Default configuration uses SQLite for easy local development.

### Production (PostgreSQL Recommended)
For production on DigitalOcean:

1. Create PostgreSQL database
2. Update `DATABASE_URL` in environment:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   ```

## 🔒 Security Recommendations

1. **Generate Secure Secret Key**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Environment Variables**
   - Never commit `.env` to version control
   - Use strong, random SECRET_KEY
   - Store API keys securely

3. **HTTPS/SSL**
   - Enable HTTPS on DigitalOcean
   - Use Let's Encrypt with Certbot
   - Configure secure cookies

4. **Database**
   - Use PostgreSQL in production
   - Regular backups
   - Restrict access to database

## 📊 Health Check

Monitor application health:

```bash
curl http://localhost:5000/health
# Response: {"status": "healthy"}
```

## 🚀 Future Enhancements

- [ ] Admin panel for service management
- [ ] Complete Stripe payment integration
- [ ] Email notifications for orders
- [ ] User accounts and order history
- [ ] Inventory management
- [ ] Advanced analytics
- [ ] Multiple currency support
- [ ] Bulk order discounts

## 🐛 Troubleshooting

### Database Errors
```bash
# Clear and recreate database
rm ecommerce.db
python -m flask run
```

### Import Errors
```bash
# Ensure dependencies are installed
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Use different port
python -m flask run --port 5001
```

### Docker Issues
```bash
# Rebuild containers
docker-compose down
docker-compose up --build
```

## 📝 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_APP` | `wsgi.py` | Flask entry point |
| `FLASK_ENV` | `development` | Environment mode |
| `SECRET_KEY` | Generated | Session secret (CHANGE IN PRODUCTION) |
| `DEBUG` | `True` | Debug mode |
| `DATABASE_URL` | `sqlite:///ecommerce.db` | Database connection |
| `STRIPE_PUBLIC_KEY` | - | Stripe public API key |
| `STRIPE_SECRET_KEY` | - | Stripe secret API key |

## 📚 Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Stripe API Reference](https://stripe.com/docs/api)
- [Docker Documentation](https://docs.docker.com/)
- [DigitalOcean Documentation](https://docs.digitalocean.com/)

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests.

## ❓ Support

For issues and questions:
- Create an issue in the repository
- Email: support@propsworks.com

---

**Last Updated**: February 2026

**Status**: Production-Ready E-Commerce Platform

