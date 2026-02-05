# Item Management Implementation Summary

## What's Been Added

### 1. Database Model Updates (`app/models.py`)
The `Service` model now includes:
- **`price_base`** (Float, nullable) - Base price (NULL = Contact for Quote)
- **`media_gallery`** (JSON) - Stores list of uploaded photos/videos with URLs and captions
- **`bulk_pricing`** (JSON) - Stores quantity-based pricing tiers with `min_quantity` and `price`
- **`variants`** (JSON) - Stores product variants with `name`, `price` (nullable), `description`, `sku`, and `is_available` flag
- **`requires_quote()`** method - Returns True if item needs a quote (price_base is None)
- **`get_price_for_quantity(quantity)`** method - Calculates price based on order quantity (returns None if quote required)

### 2. Admin Routes (`app/admin.py`)
New endpoints for item management:
- `GET /admin/items` - Item management page
- `GET /admin/api/items` - List all items (with optional category filter)
- `GET /admin/api/items/<id>` - Get specific item details
- `POST /admin/api/items` - Create new item
- `PUT /admin/api/items/<id>` - Update existing item
- `DELETE /admin/api/items/<id>` - Delete item
- `POST /admin/api/items/<id>/upload-media` - Upload photos/videos
- `DELETE /admin/api/items/<id>/media/<index>` - Delete media from item

### 3. Admin Interface (`templates/admin/items.html`)
Complete item management UI featuring:
- **Item Grid Display** - Visual cards showing all items with images and prices
- **Category Filtering** - Easy filtering by Industrial Design, 3D Printing, or Laser Engraving
- **Add/Edit Modal** - Form for creating and editing items with sections for:
  - Basic information (name, category, descriptions)
  - Pricing (base price, bulk tiers)
  - Product variants (different versions with separate pricing)
  - Media gallery (upload and manage photos/videos)
  - Active/Inactive status toggle
- **Bulk Pricing Manager** - Add/remove quantity-based discount tiers
- **Product Variants Manager** - Add/remove product variants with individual prices and SKUs
- **Media Upload** - Drag-and-drop file upload with caption support
- **Responsive Design** - Works on desktop and mobile devices

### 4. Integration with Dashboard
- Added "Manage Items" button to the admin dashboard header
- Easy navigation between content editor and item manager

### 5. Supporting Files
- **Static Upload Directory** - `/static/uploads/` for storing media files
- **Dependencies** - Added `python-slugify==8.0.1` to requirements.txt
- **Documentation** - Comprehensive guide in `ITEM_MANAGEMENT.md`

## Key Features

### Contact for Quote Option
Instead of displaying a price and "Add to Cart" button, items can be configured to show "Contact for Quote":
- Set at item level (base item doesn't have a price)
- Set at variant level (individual variants can require quotes)
- Useful for custom projects, enterprise sales, or made-to-order items
- Price field becomes optional when Contact for Quote is enabled

### Pricing Systems
Items can use:
1. **Fixed base price** - Standard pricing model
2. **Contact for Quote** - No price, customer must request quote
3. **Variants with mixed pricing** - Some variants have prices, others require quotes

### Bulk Pricing System
```python
# Example: $500 base price with bulk discounts
Tier 1: 10+ items @ $450
Tier 2: 25+ items @ $400
Tier 3: 50+ items @ $350

# Prices calculated automatically during checkout
5 items:  5 × $500 = $2,500
10 items: 10 × $450 = $4,500
25 items: 25 × $400 = $10,000
50 items: 50 × $350 = $17,500
```

### Product Variants System
```python
# Example: T-Shirt with size variants (mixed pricing)
Base Price: Not used when variants exist

Variants:
- Small: $25 (fits XS-S)
- Medium: $25 (fits M-L)
- Large: $27 (fits XL-XXL)
- Extra Large: Contact for Quote (custom sizing available)

# Each variant has:
- Unique name/identifier
- Price (or Contact for Quote)
- Optional description/notes
- Optional SKU for tracking
- Availability flag (can disable specific variants)

# Variants work with bulk pricing:
Customer selects "Large" variant ($27)
Orders 10+ units
Bulk pricing applies (if configured): 10 × $24 = $240
```

### Media Management
- Support for photos: PNG, JPG, JPEG, GIF, WEBP
- Support for videos: MP4, WEBM, MOV, AVI
- Multiple media per item
- Captions for each media file
- Easy delete functionality
- Automatic file handling and organization

### Item Organization
- Three main categories:
  - Industrial Design
  - 3D Printing
  - Laser Engraving
- Active/Inactive toggle for visibility
- Automatic slug generation from item names
- Timestamps for tracking creation

## How to Use

### Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Log in to admin panel: `/admin/login`
3. Click "Manage Items" button
4. Click "Add New Item" to create first item

### Creating an Item
1. Fill in **Basic Information** section
2. Set **Base Price** and optional **Image URL**
3. Add **Bulk Pricing Tiers** (optional but recommended)
4. Add **Product Variants** (optional for multi-version items)
5. Upload **Photos/Videos** (optional)
6. Click **Save Item**

### Managing Product Variants
- Click **"Add Variant"** to add a version of the product
- Specify variant **Name** (e.g., Small, Medium, Large)
- Set the **Price** for this specific variant
- Optionally add **Description** (dimensions, materials, colors, etc.)
- Optionally add **SKU** for inventory tracking
- Toggle **Available for purchase** to enable/disable the variant
- Remove variants with the **"Delete Variant"** button

**Use cases for variants:**
- Different sizes (Small, Medium, Large)
- Different colors (Red, Blue, Green)
- Different materials (Wood, Metal, Plastic)
- Different finishes (Matte, Glossy, Textured)
- Different configurations with different turnaround times

### Managing Bulk Pricing
- Click **"Add Pricing Tier"** to add quantity discounts
- Specify minimum quantity and reduced price
- Example: 10 units at $450 instead of $500
- Remove tiers with the **"Remove"** button

### Uploading Media
1. Click upload area or drag files
2. Add optional caption
3. Click **"Upload Media"** button
4. Media appears immediately in gallery
5. Hover to delete if needed

## File Structure

```
website3/
├── app/
│   ├── models.py           (Updated with media_gallery, bulk_pricing, variants)
│   ├── admin.py            (Item management routes added)
│   └── __init__.py         (Already configured properly)
├── templates/
│   └── admin/
│       ├── items.html      (New item management interface with variants UI)
│       └── dashboard.html  (Updated with Manage Items link)
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/            (New directory for media files)
├── requirements.txt        (Added python-slugify)
└── ITEM_MANAGEMENT.md      (Comprehensive guide including variants)
```

## Security Considerations

### File Uploads
- Only allowed file types (images and videos)
- Secure filename generation using `werkzeug.utils.secure_filename`
- Files stored in `/static/uploads/` with timestamp-based naming
- File size limits can be configured in Flask config

### Admin Access
- All item management routes require login (`@login_required` decorator)
- Admin password protection already in place
- All API endpoints protected

### Data Validation
- Required fields: name, category, description
- Price validation: Either base price or "Contact for Quote" must be selected
- Price must be >= 0 if set
- Quantity validation for bulk pricing (must be > 0)
- Variant validation:
  - Variant name required when variant exists
  - Variant must have either price or "Contact for Quote" selected
  - Variant price must be >= 0 if set
  - SKU is optional
  - Description is optional
- Category validation against predefined list
- Duplicate name check (via slug uniqueness)

## Database Migration

The database schema is automatically updated on app startup:
- `db.create_all()` creates new tables/columns
- Service model now has `media_gallery`, `bulk_pricing`, and `variants` JSON columns
- No migration files needed (using SQLAlchemy directly)

## Next Steps After Implementation

1. **Test the interface** - Add a test item and verify it appears correctly
2. **Test variants** - Create an item with 2-3 variants and verify all are editable
3. **Upload sample media** - Test photo and video uploads
4. **Test bulk pricing** - Verify price calculation during checkout
5. **Test variant pricing** - Verify variant prices display and are selectable
6. **Customize categories** - Modify if needed in admin.py (line ~203)
4. **Customize categories** - Modify if needed in admin.py (line ~203)
5. **Frontend integration** - Update catalog/detail pages to use new media gallery
6. **Customer testing** - Have users test the shopping experience
7. **Monitor performance** - Check server logs for any issues

## Troubleshooting

If items don't appear:
1. Check that item.is_active = true
2. Verify category is correct
3. Clear browser cache (Ctrl+Shift+R)
4. Check database connection
5. Review browser console for JavaScript errors

If media won't upload:
1. Verify file format is supported
2. Check file size (keep under 10MB for videos)
3. Ensure item is saved before uploading media
4. Check `/static/uploads/` directory exists and is writable

## Documentation

Full user guide available in `ITEM_MANAGEMENT.md` with:
- Step-by-step instructions
- Pricing strategy tips
- Media best practices
- API endpoint reference
- Troubleshooting guide
