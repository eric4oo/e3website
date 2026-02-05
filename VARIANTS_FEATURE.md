# Product Variants Feature Implementation

## Overview

A new **Product Variants** feature has been added to the Item Manager, allowing you to optionally include different versions of the same product that may differ in price, size, color, material, or any other distinguishing characteristic.

## What Was Added

### 1. Database Model Update (`app/models.py`)

Added a new `variants` JSON column to the `Service` model:

```python
variants = db.Column(db.JSON, default=list)
# Stores product variants: [{'name': 'Small', 'price': 100, 'description': '...', 'sku': '...', 'is_available': True}]
```

Each variant object contains:
- **`name`** (string, required) - The variant identifier (e.g., "Small", "Large", "Red")
- **`price`** (float, required) - The price for this specific variant
- **`description`** (string, optional) - Details about the variant (e.g., "5x5 inches", "Fits XL-XXL")
- **`sku`** (string, optional) - SKU or item code for inventory tracking
- **`is_available`** (boolean) - Whether this variant is available for purchase

### 2. Admin API Routes (`app/admin.py`)

Updated three endpoints to handle variants:

- **`POST /admin/api/items`** - Create new item with variants
- **`GET /admin/api/items`** - Returns all items including their variants
- **`GET /admin/api/items/<id>`** - Returns item details including variants
- **`PUT /admin/api/items/<id>`** - Update item and its variants

All endpoints automatically handle the variants JSON data.

### 3. Admin UI (`templates/admin/items.html`)

#### Added CSS Styles
- `.variants-section` - Container for variants section
- `.variant-item` - Individual variant card styling
- `.variant-controls` - Controls for managing variants
- All supporting styles for inputs and buttons

#### Added HTML Form Section
- New "Product Variants (Optional)" section in the item form
- "Add Variant" button to create new variants
- For each variant:
  - Variant Name input (required when variant exists)
  - Price input (required, numeric)
  - Description/Notes textarea (optional)
  - SKU/Item Code input (optional)
  - "Available for purchase" checkbox
  - Delete button to remove variant

#### Added JavaScript Functions
- **`addVariant(name, price, description, sku, is_available)`** - Dynamically creates a new variant form row
- Updated **`editItem()`** - Now loads and displays existing variants
- Updated **`openAddItemModal()`** - Clears variants when creating new item
- Updated **`saveItem()`** - Collects and submits variant data

### 4. Documentation Updates

Updated two documentation files:

#### `ITEM_MANAGEMENT.md`
- Added "Product Variants (Optional)" section explaining:
  - How to add variants
  - Fields for each variant
  - When to use variants (sizes, colors, materials, finishes, etc.)
  - How variants interact with bulk pricing

#### `ITEM_MANAGEMENT_IMPLEMENTATION.md`
- Updated database model documentation
- Added product variants system explanation with examples
- Updated "Creating an Item" section with variant steps
- Added "Managing Product Variants" subsection
- Updated "Next Steps" to include variant testing
- Added variant validation to "Data Validation" section

## How to Use

### Adding Variants to a New Item

1. In the Item Manager, click "Add New Item"
2. Fill in basic information and pricing
3. Scroll to the "Product Variants (Optional)" section
4. Click "Add Variant" button
5. Fill in:
   - **Variant Name** - e.g., "Small", "Red", "Oak Wood"
   - **Price** - The price for this variant
   - **Description** - Optional details (e.g., dimensions, specifications)
   - **SKU** - Optional inventory code
   - Check "Available for purchase" to enable this variant
6. Click "Add Variant" to add more variants
7. Click "Save Item" - all variants will be saved together

### Editing Existing Variants

1. Find the item and click "Edit"
2. Scroll to the "Product Variants" section
3. Modify any variant fields
4. Click "Delete Variant" to remove a variant
5. Click "Save Item" to apply changes

### Deleting Variants

- Click the "Delete Variant" button on any variant card
- The variant will be removed when you save the item

## Use Cases

### Examples Where Variants Are Useful

**T-Shirt Product:**
```
Small - $25 - Fits XS-S
Medium - $25 - Fits M-L
Large - $27 - Fits XL-XXL
Extra Large - $30 - Fits XXXL+
```

**Custom Brackets:**
```
Steel - $150 - Powder coated steel, 5 day turnaround
Aluminum - $120 - Anodized aluminum, 3 day turnaround
Stainless Steel - $200 - Food grade, 7 day turnaround
```

**Laser Engraving Service:**
```
Small 4x4 - $50 - Up to 4x4 inches
Medium 8x8 - $100 - Up to 8x8 inches
Large 12x12 - $150 - Up to 12x12 inches
```

**3D Printing Job:**
```
Low Detail (0.2mm) - $200 - Faster printing
High Detail (0.1mm) - $350 - Finer details
Ultra Detail (0.05mm) - $500 - Maximum precision
```

## How Variants Interact With Other Features

### Variants + Bulk Pricing

Both features can be used together. Example:

```
Item: Custom Bracket

Variant 1 (Steel): $150
  - If ordering 10+: Bulk pricing applies (e.g., $135)
  - Final price: 10 × $135 = $1,350

Variant 2 (Aluminum): $120
  - If ordering 10+: Bulk pricing applies (e.g., $108)
  - Final price: 10 × $108 = $1,080
```

The customer first selects a variant (choosing the price), then bulk pricing applies to that variant's price.

### Variants + Media Gallery

Media gallery is attached to the main item, not individual variants. If you have multiple variants, the same photos/videos apply to all. This is useful for showing different angles or the product in different use cases.

### Variants + Base Price

When an item has variants, the base price is typically not displayed to customers. Instead, the variant prices are shown. The base price can be used as a default or template.

## Data Structure

### In Database (JSON)

```json
{
  "variants": [
    {
      "name": "Small",
      "price": 25,
      "description": "Fits XS-S",
      "sku": "TSHIRT-S",
      "is_available": true
    },
    {
      "name": "Large",
      "price": 27,
      "description": "Fits XL-XXL",
      "sku": "TSHIRT-L",
      "is_available": true
    },
    {
      "name": "Extra Large",
      "price": 30,
      "description": "Fits XXXL+",
      "sku": "TSHIRT-XL",
      "is_available": false
    }
  ]
}
```

### In API Response

The API returns items with variants in the JSON response:

```json
{
  "id": 1,
  "name": "T-Shirt",
  "price_base": 25,
  "variants": [
    {
      "name": "Small",
      "price": 25,
      "description": "Fits XS-S",
      "sku": "TSHIRT-S",
      "is_available": true
    },
    ...
  ]
}
```

## Validation

The system validates variants during save:

- **Variant name** is required when any variant exists
- **Variant price** is required and must be >= 0
- **SKU** is optional but should be unique (enforcement at application level recommended)
- **Description** is optional
- Empty or incomplete variants are skipped during save

## Disabling Variants

You can disable individual variants without deleting them:

1. Edit the item
2. Uncheck "Available for purchase" on the variant
3. Save the item
4. That variant won't be available to customers but the data is preserved

This is useful for temporary unavailability (e.g., seasonal items, stock issues).

## Best Practices

### When to Use Variants

Use variants when you have the following scenario:
- Same base product
- Different options available
- Different pricing for different options
- Want to show all options together

### When NOT to Use Variants

- Different products entirely - create separate items
- Options with same price - consider using description instead
- One main product with rare custom requests - handle via contact form

### Naming Conventions

Keep variant names clear and consistent:
- ✅ "Small", "Medium", "Large"
- ✅ "Red", "Blue", "Green"
- ✅ "Wood", "Metal", "Plastic"
- ✅ "Matte", "Glossy", "Textured"
- ❌ "1", "2", "3" (not descriptive)
- ❌ "Option A", "Option B" (too generic)

### SKU Recommendations

Use SKU consistently for inventory tracking:
- Include base product code: `TSHIRT-S`, `TSHIRT-M`, `TSHIRT-L`
- Or use hierarchical system: `001-SIZE-1`, `001-SIZE-2`
- Keep them short and memorable
- Use for integration with inventory systems

## Limitations

Currently, variants:
- Cannot have different images (use media gallery for main product)
- Cannot have different media galleries per variant
- Are not integrated with inventory/stock tracking
- Must be managed in admin panel (no frontend-managed updates yet)

These features could be added in future updates.

## Testing

To test the variants feature:

1. **Create an item with variants**
   - Go to Add New Item
   - Add 2-3 variants with different names and prices
   - Save and verify variants are stored

2. **Edit variants**
   - Click Edit on the item
   - Modify a variant name/price
   - Delete a variant
   - Add a new variant
   - Save and verify changes

3. **Test availability flag**
   - Create a variant
   - Uncheck "Available for purchase"
   - Save and verify it's marked as unavailable

4. **Test with bulk pricing**
   - Create item with variants and bulk pricing tiers
   - Save and verify both are stored
   - (Note: Frontend integration for variant selection pending)

## Frontend Integration (Future)

The variants data is now available in the API for frontend use. To integrate variants into your product pages:

1. **Get item with variants**: `GET /admin/api/items/<id>`
2. **Display variant selector**: Create dropdown or radio buttons
3. **Update price dynamically**: When variant is selected
4. **Add to cart with variant**: Include selected variant in cart item data

Example integration in `routes.py`:

```python
# Return item with variants to catalog/detail pages
@app.route('/api/products/<int:product_id>')
def get_product(product_id):
    item = Service.query.get_or_404(product_id)
    return jsonify({
        'id': item.id,
        'name': item.name,
        'price_base': item.price_base,
        'variants': item.variants,
        # ... other fields
    })
```

## Support & Troubleshooting

### Variants Not Saving

1. Verify all required fields are filled (name and price)
2. Check that prices are valid numbers
3. Ensure main item fields are all filled
4. Save again - may need to refresh page

### Variants Not Displaying

1. Refresh the page (Ctrl+Shift+R)
2. Check that item is Active
3. Verify variants were actually saved
4. Check browser developer console for errors

### Missing Variants When Editing

1. The variants are still in the database
2. Try refreshing the page
3. Clear browser cache
4. Check application logs

## Files Modified

- `app/models.py` - Added variants column to Service model
- `app/admin.py` - Updated API endpoints to handle variants
- `templates/admin/items.html` - Added variants UI and JavaScript
- `ITEM_MANAGEMENT.md` - Added variants documentation
- `ITEM_MANAGEMENT_IMPLEMENTATION.md` - Updated implementation docs

## Summary

The Product Variants feature provides a simple yet powerful way to manage products with multiple options. It integrates seamlessly with existing bulk pricing and media gallery features, gives you full control in the admin panel, and is ready for frontend integration when you're ready to display variants to customers.
