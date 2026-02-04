# PropsWorks Deployment Checklist

## Pre-Deployment Tasks

### 1. Security Setup
- [ ] Generate secure SECRET_KEY
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- [ ] Update .env with generated key
- [ ] Remove .env from version control (verify .gitignore)
- [ ] Generate strong passwords for database

### 2. Service Catalog Setup
- [ ] Add Industrial Design services to database
- [ ] Add 3D Printing services to database
- [ ] Add Laser Engraving services to database
- [ ] Set competitive pricing for each service
- [ ] Add service images/descriptions

### 3. Payment Integration
- [ ] Create Stripe account (https://stripe.com)
- [ ] Get Stripe API keys
- [ ] Add STRIPE_PUBLIC_KEY to .env
- [ ] Add STRIPE_SECRET_KEY to .env
- [ ] Test payment flow (Stripe test mode)
- [ ] Implement payment processing in checkout

### 4. Contact Information
- [ ] Update contact email (currently: info@propsworks.com)
- [ ] Update phone number (currently: (555) 123-4567)
- [ ] Add contact form or email integration
- [ ] Setup email notifications for new orders

### 5. Database Setup
- [ ] Local: Verify SQLite database creation
- [ ] Production: Setup PostgreSQL on DigitalOcean
- [ ] Database backups configured
- [ ] Test data migration if needed

## DigitalOcean Deployment

### Option A: App Platform (Recommended)

1. **Prepare Repository**
   - [ ] Push code to GitHub
   - [ ] Ensure .env is in .gitignore
   - [ ] Verify Dockerfile is present

2. **DigitalOcean Setup**
   - [ ] Create DigitalOcean account
   - [ ] Create new App
   - [ ] Connect GitHub repository
   - [ ] Select main branch

3. **Configure Environment**
   - [ ] Set FLASK_ENV=production
   - [ ] Set SECRET_KEY (from step 1)
   - [ ] Set STRIPE_PUBLIC_KEY
   - [ ] Set STRIPE_SECRET_KEY
   - [ ] Set DATABASE_URL (if using external DB)

4. **Deploy**
   - [ ] Click Deploy
   - [ ] Wait for deployment to complete
   - [ ] Test all routes
   - [ ] Check logs for errors

### Option B: Droplet

1. **Create Droplet**
   - [ ] Choose Ubuntu 22.04 LTS
   - [ ] Select appropriate size (start with $5-10/month)
   - [ ] Add SSH key
   - [ ] Create Droplet

2. **Setup Server**
   - [ ] SSH into droplet
   - [ ] Install Docker
   - [ ] Install Docker Compose
   - [ ] Clone repository
   - [ ] Create .env with production values

3. **Deploy Application**
   - [ ] Build Docker image
   - [ ] Run Docker container with proper environment
   - [ ] Setup Nginx reverse proxy
   - [ ] Configure SSL/HTTPS with Let's Encrypt

4. **Monitor**
   - [ ] Check container logs
   - [ ] Test health endpoint
   - [ ] Setup monitoring/alerts

## Testing Checklist

### Local Testing
- [ ] Home page loads correctly
- [ ] Services catalog displays
- [ ] Category filtering works
- [ ] Service detail pages work
- [ ] Add to cart functionality works
- [ ] Cart displays correctly
- [ ] Checkout form displays
- [ ] All links work
- [ ] Mobile responsive on small screens
- [ ] All pages load without errors

### Production Testing
- [ ] HTTPS working
- [ ] Home page loads
- [ ] Services display correctly
- [ ] Cart functionality works
- [ ] Email notifications sent
- [ ] Database queries perform well
- [ ] No console errors
- [ ] Performance acceptable

## Monitoring Setup

- [ ] Enable DigitalOcean monitoring
- [ ] Setup health check alerts
- [ ] Configure log aggregation
- [ ] Setup database backups
- [ ] Create incident response plan

## Post-Deployment

### Day 1
- [ ] Monitor error logs
- [ ] Check for performance issues
- [ ] Verify all pages load correctly
- [ ] Test complete user flow

### Week 1
- [ ] Gather user feedback
- [ ] Monitor server load
- [ ] Check database performance
- [ ] Review security logs

### Ongoing
- [ ] Regular backups
- [ ] Security updates
- [ ] Performance monitoring
- [ ] Customer support

## Admin Tasks

- [ ] Setup admin panel (future feature)
- [ ] Create order management system
- [ ] Setup email notifications
- [ ] Create service management interface
- [ ] Setup analytics/reporting

## Marketing Setup

- [ ] Update social media links
- [ ] Create email template for notifications
- [ ] Setup contact form
- [ ] Create FAQ section
- [ ] Add testimonials section
- [ ] SEO optimization

## Documentation

- [ ] Update README with live URL
- [ ] Create API documentation
- [ ] Document service categories
- [ ] Create troubleshooting guide
- [ ] Document deployment process

---

## Quick Deployment Command

```bash
# For DigitalOcean App Platform:
git push origin main
# Then deploy through DigitalOcean dashboard

# For Droplet:
docker build -t propsworks:latest .
docker run -d -p 80:8000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your_key_here \
  -e STRIPE_PUBLIC_KEY=pk_... \
  -e STRIPE_SECRET_KEY=sk_... \
  --restart always \
  propsworks:latest
```

---

## Support Resources

- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Stripe: https://stripe.com/docs
- DigitalOcean: https://docs.digitalocean.com/
- Docker: https://docs.docker.com/

---

**Last Updated:** February 2026
