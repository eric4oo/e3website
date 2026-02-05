# Shipping Integration Setup Guide

## Overview

Your e-commerce platform now includes real-time shipping rate calculation using Canada Post's Commercial API. The system allows customers to select from multiple shipping methods during checkout.

## Current Implementation

### Features Implemented

✅ **Real-Time Shipping Rates** - Calculate shipping costs based on:
- Origin postal code: N9J 1V6 (configured in `app/shipping.py`)
- Destination postal code (entered by customer at checkout)
- Package weight (calculated from product weights)

✅ **Shipping Method Selection** - Customers can choose from:
- Regular Parcel (DOM.RP) - 3-5 business days
- Express (DOM.EP) - 1-2 business days
- Xpresspost (DOM.XP) - Next business day
- Priority (DOM.PRIORITY) - Overnight delivery

✅ **Demo Rates** - While working without API credentials, the system uses realistic estimates based on Canada Post standard pricing

✅ **Seamless Checkout** - Shipping cost is automatically calculated and added to the order total

✅ **Order Records** - Shipping method and cost are stored with each order for tracking and fulfillment

## Setting Up Canada Post Integration

### Step 1: Get Canada Post Commercial API Credentials

1. Visit [Canada Post Business Portal](https://www.canadapost.ca/business)
2. Navigate to **Shipping Solutions** → **eParcel API**
3. Sign up for a Business Account (if you don't have one)
4. Request API access with the following information:
   - Customer Number: Canada Post will provide this
   - API Username: You create this
   - API Password: You create this

**Documentation**: [Canada Post eParcel API Guide](https://www.canadapost.ca/tools/pg/manual/PG_eParcel_001e.pdf)

### Step 2: Configure Environment Variables

Add your Canada Post credentials to your `.env` file (create one if it doesn't exist):

```env
CANADA_POST_USERNAME=your_api_username_here
CANADA_POST_PASSWORD=your_api_password_here
CANADA_POST_CUSTOMER_NUMBER=your_customer_number_here
```

**Important**: Restart your Flask application after adding these variables.

### Step 3: Update Origin Postal Code

The system is currently configured with origin: `N9J 1V6`

To change this to your actual business location:

**File:** `app/shipping.py`

Find this line (around line 27):
```python
ORIGIN_POSTAL_CODE = "N9J1V6"  # User's location
```

Replace with your postal code:
```python
ORIGIN_POSTAL_CODE = "YOUR_POSTAL_CODE"  # Your location
```

### Step 4: Test the Integration

1. Make sure your `.env` file is in the root directory
2. Start your Flask app
3. Go to checkout and enter a destination postal code
4. Verify shipping rates are calculated
5. Check if rates update based on postal code changes

## Demo Mode

If you don't have Canada Post API credentials yet, the system will automatically use **demo rates** that are based on actual Canada Post pricing:

- Regular Parcel: $8.95 + $0.50/kg
- Express: $16.45 + $1.00/kg
- Xpresspost: $24.95 + $1.50/kg
- Priority: $35.95 + $2.00/kg

Demo mode is indicated by a note on the checkout page: *"Demo rates: Add Canada Post API credentials for real-time pricing"*

## How Shipping Works on Your Site

### For Customers

1. **Add items to cart** - Each product has a weight value (`weight_kg`)
2. **Go to checkout** - Fill in shipping address with postal code
3. **Automatic rate calculation** - Postal code triggers real-time rate lookup
4. **Choose preferred method** - Radio buttons show all available options
5. **See updated total** - Shipping cost is added to order total
6. **Complete payment** - Order includes shipping method and cost

### For Orders

Each order now stores:
- `shipping_method`: Code (e.g., 'DOM.RP')
- `shipping_service_name`: Display name (e.g., 'Regular Parcel')
- `shipping_cost`: Amount charged
- `subtotal`: Product cost before shipping
- `total_amount`: Final amount including shipping

## Technical Details

### Model Changes

**Service Model** (`app/models.py`):
- Added `weight_kg` field (default: 0.5 kg)
- Used for calculating shipping rates

**Order Model** (`app/models.py`):
- Added `shipping_method`: Shipping service code
- Added `shipping_service_name`: Display name
- Added `shipping_cost`: Cost of selected method
- Added `subtotal`: Product total before shipping
- Updated `total_amount`: Now includes shipping

### API Endpoint

**POST** `/services/api/shipping-rates`

Request:
```json
{
    "destination_postal_code": "N9J 1V6",
    "domestic_only": true
}
```

Response:
```json
{
    "success": true,
    "origin": "N9J1V6",
    "destination": "N9J1V6", 
    "weight_kg": 2.5,
    "options": [
        {
            "service_code": "DOM.RP",
            "service_name": "Regular Parcel",
            "price": 10.20,
            "guaranteed_days": "3-5",
            "est_delivery_date": "Approximately 3-5 business days"
        },
        ...
    ]
}
```

## Product Weight Configuration

To update product weights in the admin panel or database:

**Database SQL**:
```sql
UPDATE services SET weight_kg = 1.5 WHERE id = 1;
```

**Python** (in app code):
```python
service = Service.query.get(1)
service.weight_kg = 1.5
db.session.commit()
```

## API Rate Limits

Canada Post API has the following limits:
- **Requests**: Up to 2,500 per day
- **Response time**: Typically < 1 second
- **Countries**: Canada domestic and select international destinations

## Troubleshooting

### Shipping Rates Not Calculating

1. **Check postal code format**: Must be "A1A 1A1" or "A1A1A1"
2. **Verify API credentials**: Review `.env` file
3. **Check Flask console**: Look for error messages
4. **Test with postal code in Ontario/British Columbia**: Some areas may have limited coverage

### "Invalid postal code" Error

- Ensure postal code is valid Canadian format
- Remove any extra spaces before/after
- Canada Post API doesn't support international searches (currently domestic only)

### "Credentials not configured" Error

- Add credentials to `.env` file
- Verify environment variables are loaded
- Restart Flask application after adding `.env`

## Future Enhancements

Potential features to add:

1. **International Shipping** - Add support for INTL.* services
2. **Tracking Integration** - Pull tracking info from Canada Post after shipping
3. **Label Generation** - Programmatically generate shipping labels
4. **Regional Pricing** - Different rates for different provinces
5. **Shipping Insurance** - Optional insurance options
6. **Free Shipping Threshold** - Free shipping for orders over $X
7. **Scheduled Pickups** - Auto-schedule Canada Post pickups
8. **Admin Dashboard** - View shipment status and tracking

## Support

For questions about Canada Post API:
- [Canada Post Developer API](https://www.canadapost.ca/tools/app/en/business/tools/pg/manual)
- Canada Post Business Support: 1-800-267-1133

For issues with your implementation:
- Check error logs in Flask console
- Verify `.env` file exists and has correct format
- Test with demo rates first before troubleshooting API

## Files Modified

- `app/models.py` - Added shipping fields to Order and Service models
- `app/services.py` - Added `/api/shipping-rates` endpoint
- `app/shipping.py` - NEW: Canada Post integration service
- `templates/services/checkout.html` - Added shipping selection UI
- `templates/services/order_confirmation.html` - Display shipping info
- `requirements.txt` - Added `requests` library
