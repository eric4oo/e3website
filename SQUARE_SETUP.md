# Square Payment Integration Setup Guide

## Status: ✅ CONFIGURED AND READY

Your PropsWorks e-commerce platform is fully configured for Square payment processing.

---

## What's Been Set Up

### 1. **Backend Integration**
- ✅ Square Python SDK (squareup) added to requirements
- ✅ Payment processing module (`app/payment.py`) created
- ✅ Square payment route (`/services/process-payment`) configured
- ✅ Order confirmation page with payment details

### 2. **Database**
- ✅ Order model updated with Square payment fields:
  - `square_payment_id` - Stores Square payment ID
  - `square_order_id` - Stores Square order ID (optional)
  - Customer address, phone, city, state, zip

### 3. **Frontend**
- ✅ Checkout page with Square Web Payments SDK
- ✅ Secure payment form integrated
- ✅ Order confirmation page created
- ✅ Payment error handling

### 4. **Configuration**
- ✅ Square environment variables in `.env`
- ✅ Configuration classes updated
- ✅ Payment processor factory function ready

---

## Getting Your Square Credentials

### Step 1: Create Square Account
1. Go to https://squareup.com
2. Sign up for an account
3. Complete the onboarding process

### Step 2: Get Your API Keys
1. Log in to Square Dashboard: https://square.com/app/dashboard
2. Click **Settings** (bottom left)
3. Select **Developer** → **API Keys**
4. You'll see two environments:
   - **Sandbox** (for testing)
   - **Production** (for live payments)

### Step 3: Copy Your Credentials

**For Sandbox (Testing):**
- Application ID: Starts with `sq_test_`
- Access Token: Starts with `sq_atp_test_`

**For Production (Live):**
- Application ID: Starts with `sq_`
- Access Token: Starts with `sq_atp_`

### Step 4: Get Your Location ID
1. In Square Dashboard, click **Locations** (left menu)
2. Your location ID appears next to your business name
3. It looks like: `L1234567890ABC`

---

## Updating Your .env File

Edit `.env` in your project root and add your Square credentials:

```bash
# Square Payment Settings
SQUARE_APPLICATION_ID=sq_test_your_actual_id_here
SQUARE_ACCESS_TOKEN=sq_atp_test_your_actual_token_here
SQUARE_ENVIRONMENT=sandbox
SQUARE_LOCATION_ID=L1234567890ABC
```

**Important:**
- Use `sandbox` for testing
- Switch to `production` only when ready for live payments
- Keep these values secure - never commit to version control

---

## How It Works

### Checkout Flow

1. **Customer adds items to cart**
   - Services added with pricing

2. **Customer proceeds to checkout**
   - Fills in shipping information
   - Enters payment details using Square Web Payments SDK

3. **Payment Processing**
   - Customer clicks "Pay Now"
   - Square Web Payments SDK securely tokenizes card
   - Nonce sent to your backend
   - Backend processes payment with Square API
   - Payment confirmation received

4. **Order Created**
   - Order saved to database with:
     - Customer information
     - Square payment ID
     - Payment status (paid/failed)
   - Order confirmation email sent

5. **Order Confirmation**
   - Customer sees confirmation page
   - Order number and details displayed
   - Receipt information available

---

## Payment Processing Features

### ✅ Implemented

```python
# Process payment with Square
processor = get_square_processor()
result = processor.process_payment(
    amount_cents=1000,  # $10.00
    source_id=nonce     # From Web Payments SDK
)

# Refund payment
processor.refund_payment(
    payment_id='sq_payment_id',
    amount_cents=1000   # Optional - full refund if not specified
)

# Retrieve payment details
processor.get_payment(payment_id='sq_payment_id')
```

### 🔐 Security Features

- PCI Compliance: Square handles card data encryption
- Idempotency: Duplicate payment protection
- Error handling: Comprehensive error messages
- Logging: Payment processing logged for debugging

---

## Testing

### Test Card Numbers (Sandbox Only)

```
Visa:              4111 1111 1111 1111
Mastercard:        5555 5555 5555 4444
American Express:  3782 822463 10005
Discover:          6011 1111 1111 1117
```

**Expiration:** Any future date (e.g., 12/25)
**CVV:** Any 3-4 digits

---

## Environment Variables Reference

| Variable | Value | Description |
|----------|-------|-------------|
| `SQUARE_APPLICATION_ID` | sq_test_... | Your Square Application ID |
| `SQUARE_ACCESS_TOKEN` | sq_atp_test_... | Your Square Access Token |
| `SQUARE_ENVIRONMENT` | sandbox/production | Testing or Live |
| `SQUARE_LOCATION_ID` | L... | Your Square Location ID |

---

## Deploying to DigitalOcean

### DigitalOcean App Platform

Add these environment variables in App Settings:

```
SQUARE_APPLICATION_ID=sq_...
SQUARE_ACCESS_TOKEN=sq_atp_...
SQUARE_ENVIRONMENT=production
SQUARE_LOCATION_ID=L...
```

### DigitalOcean Droplet

Add to `.env` on server or pass as environment variables:

```bash
export SQUARE_APPLICATION_ID=sq_...
export SQUARE_ACCESS_TOKEN=sq_atp_...
export SQUARE_ENVIRONMENT=production
export SQUARE_LOCATION_ID=L...
```

---

## Troubleshooting

### Payment Not Processing

**Issue:** 403 Unauthorized error

**Solution:**
- Verify access token is correct
- Check token hasn't expired
- Regenerate token if needed

### "Invalid source ID" Error

**Issue:** Payment fails with invalid source ID

**Solution:**
- Ensure Web Payments SDK is loaded correctly
- Verify nonce is generated before sending
- Check browser console for errors

### Sandbox vs Production Mix

**Issue:** Sandbox credentials with production environment

**Solution:**
- Test cards only work in sandbox mode
- Production cards only work in production mode
- Keep credentials separate per environment

### Payment Appears Twice

**Issue:** Duplicate payments

**Solution:**
- Idempotency key prevents duplicates
- Already handled in `payment.py`
- Check application logs

---

## Monitoring & Support

### Square Dashboard

- Track payments: https://square.com/app/payments/activity
- View orders: https://square.com/app/orders
- Monitor disputes: https://square.com/app/disputes
- Check analytics: https://square.com/app/analytics

### Resources

- Square API Docs: https://developer.squareup.com/docs
- Square Support: https://squareup.com/contact/support
- Web Payments SDK: https://developer.squareup.com/docs/web-payments/overview

### Support Contact

- PropsWorks Support: support@propsworks.com

---

## Security Best Practices

### ✅ DO:
- ✅ Use HTTPS in production
- ✅ Keep access tokens secure
- ✅ Store in environment variables
- ✅ Regenerate tokens regularly
- ✅ Monitor payment logs
- ✅ Test in sandbox first

### ❌ DON'T:
- ❌ Hardcode credentials in code
- ❌ Commit .env to version control
- ❌ Share access tokens
- ❌ Use test cards in production
- ❌ Log sensitive payment data
- ❌ Skip HTTPS in production

---

## Next Steps

1. **Create Square Account** → https://squareup.com
2. **Get API Keys** → https://square.com/app/settings/keys
3. **Update .env** with your credentials
4. **Test in Sandbox** with test card numbers
5. **Deploy to DigitalOcean**
6. **Switch to Production** when ready for live payments

---

## File Changes Made

### New Files:
- `app/payment.py` - Square payment processor

### Modified Files:
- `requirements.txt` - Added squareup SDK
- `config.py` - Added Square configuration
- `app/models.py` - Added Square fields to Order model
- `app/services.py` - Added payment processing route
- `templates/services/checkout.html` - Added Square Web Payments SDK
- `templates/services/order_confirmation.html` - Created confirmation page
- `.env` - Added Square configuration variables

---

**Last Updated:** February 4, 2026

**Status:** ✅ READY FOR USE
