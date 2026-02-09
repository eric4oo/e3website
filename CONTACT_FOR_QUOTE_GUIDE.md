# Contact for Quote Feature

## Overview

The "Contact for Quote" feature allows you to display items or variants without a set price, prompting customers to contact you for a custom quote instead of adding the item directly to their cart. This is ideal for custom projects, enterprise solutions, and made-to-order products.

## When to Use Contact for Quote

### Perfect for:
- **Custom Projects** - Where pricing depends on specifications (e.g., custom web design, architectural drawings)
- **Enterprise Sales** - Large volume orders requiring negotiation
- **Made-to-Order Items** - Products that need customization before pricing
- **Variable Scope Work** - Services where scope needs to be determined first
- **Limited/Seasonal Items** - Where availability affects pricing
- **Consultation Required** - Products/services needing expert consultation before quote

### Not ideal for:
- Standard off-shelf products with fixed pricing
- High-volume customer purchases (slows down sales process)
- Simple variations with clear pricing differences

## How to Set Up Contact for Quote

### At Item Level (Base Item)

1. In the Item Manager, click "Add New Item"
2. Fill in basic information (Name, Category, Description)
3. In the **Pricing** section, check the box **"Contact for Quote (no price set)"**
4. The price field will automatically hide
5. Leave **Image URL** if desired (optional)
6. Save the item

When activated:
- The price field is hidden and disabled
- Base price in database is set to NULL
- Item displays "Contact for Quote" instead of a price
- No "Add to Cart" button available on customer-facing pages
- Customers see a "Contact Us" button instead

### At Variant Level

1. Create an item with variants
2. Click "Add Variant" for each variation
3. For specific variants that need quotes:
   - Enter the **Variant Name** (e.g., "Custom Size", "Enterprise Edition")
   - Check **"Contact for Quote"** for that variant
   - The price field will hide
4. For standard variants with prices:
   - Enter the **Variant Name**
   - Leave "Contact for Quote" unchecked
   - Enter the **Price**
5. Save the item

Example - Mixed Pricing:
```
Variant 1: Small - $25 (standard price)
Variant 2: Medium - $45 (standard price)
Variant 3: Large - Contact for Quote (requires consultation)
Variant 4: Custom - Contact for Quote (truly custom, needs quote)
```

## Display on Admin Panel

### Item Cards Show:
- Item name, category, and description
- "Contact for Quote" in orange text (not a price)
- Number of media files, pricing tiers, and variants
- Edit/Delete buttons

Example card display:
```
Item: Custom Industrial Design
Category: Industrial Design
Description: Bespoke CAD design...
[Contact for Quote]  (in orange)
```

## Display on Website (Frontend)

When implemented on the frontend (in your catalog/detail pages), items set to "Contact for Quote" will show:

- Product/Service information as normal
- Photos and descriptions as usual
- **No price displayed** (instead shows "Contact for Quote")
- **"Request a Quote" or "Contact Us" button** instead of "Add to Cart"
- May include estimated turnaround or lead time

Example contact information that could be displayed:
```
Custom Bracket Service

Description: We create custom brackets tailored to your specifications...

[Contact for Quote]

For more information or to request a quote:
Email: info@propsworks.com
or use the contact form below
```

## Database Structure

### At Item Level

When you set Contact for Quote on an item:

```json
{
  "id": 1,
  "name": "Custom Industrial Design",
  "price_base": null,  // NULL indicates Contact for Quote
  "variants": [],
  "bulk_pricing": []
}
```

### At Variant Level

When you set Contact for Quote on individual variants:

```json
{
  "id": 2,
  "name": "Custom Brackets",
  "price_base": 150,  // Base item has a price
  "variants": [
    {
      "name": "Steel",
      "price": 150,  // Standard variant with price
      "sku": "BRACKET-STEEL",
      "is_available": true
    },
    {
      "name": "Custom Alloy",
      "price": null,  // Contact for Quote variant
      "sku": "BRACKET-CUSTOM",
      "is_available": true
    }
  ]
}
```

## API Responses

The API endpoints return items with Contact for Quote properly represented:

### GET /admin/api/items

```json
[
  {
    "id": 1,
    "name": "Custom Logo Design",
    "price_base": null,  // null = Contact for Quote
    "description": "Custom vector logo design service",
    "category": "industrial_design",
    "is_active": true,
    "variants": []
  },
  {
    "id": 2,
    "name": "T-Shirt",
    "price_base": 25,  // Item has base price
    "variants": [
      { "name": "Small", "price": 25 },
      { "name": "Large", "price": 25 },
      { "name": "Custom", "price": null }  // This variant is quote
    ]
  }
]
```

## Model Methods

The `Service` model includes helper methods for handling Contact for Quote:

### `requires_quote()` Method
```python
item = Service.query.get(1)

if item.requires_quote():
    # Show "Contact for Quote" instead of price
    display_message = "Contact for Quote"
else:
    # Show the price
    display_message = f"${item.price_base}"
```

### `get_price_for_quantity(quantity)` Method
```python
item = Service.query.get(1)

price = item.get_price_for_quantity(10)

if price is None:
    # Item requires a quote
    print("This item requires a custom quote")
else:
    # Price is available
    print(f"Price for 10: ${price}")
```

## Frontend Implementation Guide

### Displaying Items with Contact for Quote

```python
# In a route that serves catalog/detail pages
@app.route('/api/products/<int:product_id>')
def get_product(product_id):
    item = Service.query.get_or_404(product_id)
    
    product_data = {
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'media': item.media_gallery,
    }
    
    # Check if item requires quote
    if item.requires_quote():
        product_data['requires_quote'] = True
        product_data['price'] = None
    else:
        product_data['requires_quote'] = False
        product_data['price'] = item.price_base
    
    # Handle variants
    if item.variants:
        product_data['variants'] = []
        for variant in item.variants:
            product_data['variants'].append({
                'name': variant['name'],
                'price': variant.get('price'),  # Could be None
                'requires_quote': variant.get('price') is None,
                'sku': variant.get('sku'),
                'is_available': variant.get('is_available', True)
            })
    
    return jsonify(product_data)
```

### HTML/Template Example

```html
<div class="product-detail">
    <h1>{{ product.name }}</h1>
    <p>{{ product.description }}</p>
    
    {% if product.requires_quote %}
        <div class="quote-section">
            <h3>This is a Custom Quote Item</h3>
            <p>Contact us for a detailed quote based on your specific needs.</p>
            <button onclick="openContactForm()">Request a Quote</button>
        </div>
    {% else %}
        <div class="price-section">
            <span class="price">${{ product.price }}</span>
            <button onclick="addToCart()">Add to Cart</button>
        </div>
    {% endif %}
    
    <!-- Variants (if any) -->
    {% if product.variants %}
        <div class="variants">
            <label>Select Variant:</label>
            <select id="variantSelect" onchange="updateVariantPrice()">
                <option value="">Choose...</option>
                {% for variant in product.variants %}
                    <option value="{{ variant.name }}" data-price="{{ variant.price or 'quote' }}">
                        {{ variant.name }}
                        {% if variant.requires_quote %}
                            - Contact for Quote
                        {% else %}
                            - ${{ variant.price }}
                        {% endif %}
                    </option>
                {% endfor %}
            </select>
        </div>
    {% endif %}
</div>
```

## Common Scenarios

### Scenario 1: Completely Custom Service

```
Item: Custom Web Design Service
- No base price
- Contact for Quote enabled
- No variants
- No bulk pricing

Result: Customer sees "Contact for Quote" and must request quote for any project
```

### Scenario 2: Tiered Service with Entry Level

```
Item: Consulting Service
- Base price: $150/hour (for standard consulting)
- Contact for Quote: Disabled
- Variants:
  - Standard Consulting: $150/hour
  - Custom Training: Contact for Quote
  - Corporate Training: Contact for Quote
- Bulk pricing: 10+ hours @ $135/hour

Result: Some variants are standard pricing, others require custom quotes
```

### Scenario 3: Product with Limited Custom Options

```
Item: 3D Printing
- Base price: $50
- Contact for Quote: Disabled
- Variants:
  - Standard PLA: $50
  - High-Detail ABS: $100
  - Custom Materials: Contact for Quote
- Bulk pricing: 10+ prints @ 15% discount

Result: Most variants have set pricing, rarely-used custom materials quote
```

## Editing Contact for Quote Items

### Modifying an Item

1. Find the item and click Edit
2. In Pricing section:
   - To enable Contact for Quote: Check the box (price field hides)
   - To disable Contact for Quote: Uncheck the box (price field shows)
3. Adjust other fields as needed
4. Click Save

### Modifying Variants

1. Find the item and click Edit
2. Find the variant to modify
3. Check/uncheck "Contact for Quote" as needed
4. If unchecked, enter a price
5. Click Save

## Bulk Pricing with Contact for Quote

**Important:** Bulk pricing is not compatible with items that use Contact for Quote at the base level.

- **Items with Contact for Quote:** Cannot have bulk pricing tiers
- **Items with pricing:** Can have bulk pricing tiers that apply
- **Variants:** Individual variants can have Contact for Quote independent of item pricing

If you need bulk pricing:
1. Don't enable Contact for Quote on the base item
2. Set a base price
3. Add bulk pricing tiers as needed
4. Individual variants can still be set to Contact for Quote if desired

## Testing Contact for Quote

### Admin Panel Testing:

1. ✅ Create an item with Contact for Quote enabled
2. ✅ Verify "Contact for Quote" appears on the item card
3. ✅ Edit the item and verify Contact for Quote checkbox is checked
4. ✅ Create variants with mixed pricing (some with price, some Contact for Quote)
5. ✅ Verify each variant's quote status displays correctly

### Data Verification:

1. Check database that `price_base` is NULL for quote items
2. Verify variant prices are NULL for quote variants
3. Test API endpoint returns correct null values

### Frontend Integration:

1. Implement quote detection logic
2. Display "Contact for Quote" instead of price
3. Show "Request Quote" button instead of "Add to Cart"
4. Test variant selection with mixed pricing

## Best Practices

### When Setting Up Contact for Quote

1. **Be Clear** - Use descriptive names so customers understand why a quote is needed
   - ✅ "Custom Configuration" 
   - ❌ "Other"

2. **Provide Context** - Include description explaining why it requires a quote
   - ✅ "Custom designs require consultation with our team"
   - ❌ (Leave blank)

3. **Set Expectations** - Let customers know response time for quotes
   - ✅ "We respond to quote requests within 24 hours"
   - ❌ No mention of timeline

4. **Make Contact Easy** - Ensure contact information is visible
   - Display phone number
   - Display email
   - Include contact form
   - Show hours of availability

5. **Mix Strategically** - If using variants:
   - Offer some quick/standard options with pricing
   - Reserve Contact for Quote for truly custom items
   - This shows you have options for budget-conscious customers

### Communication Tips

From Customer Perspective:
- "Contact for Quote" means "This needs personalized attention"
- Expect longer response times
- Need to verify requirements before seeing price
- May require multiple conversations

As the Business:
- Use for items where customization affects price significantly
- Opportunity to upsell/understand customer needs
- Can provide value-added insight during quote process
- Builds business relationship before sale

## Troubleshooting

### Contact for Quote Not Showing

1. Verify you checked the "Contact for Quote" checkbox
2. Verify the item was saved (should see confirmation message)
3. Refresh the admin page
4. Check that item is marked as Active
5. Clear browser cache (Ctrl+Shift+R)

### Can't Uncheck Contact for Quote

1. Make sure you have a price entered first (if transitioning to pricing)
2. Uncheck the box
3. Click in the price field and enter a value
4. Save the item

### Mixed Pricing Not Working on Variants

1. Verify each variant has a name (required)
2. Verify each variant has either a price OR "Contact for Quote" checked
3. Don't leave both empty
4. Save the item
5. Edit again to verify changes saved

### API Returns Wrong Status

1. Item requires quote but `price_base` is 0 instead of null
   - Edit item, enable Contact for Quote, save
2. Variant requires quote but `price` is 0 instead of null
   - Edit variant, enable Contact for Quote, save

## Future Enhancements

Potential improvements for future versions:
- Quote request form integrated into product page
- Email notifications when quote requested
- Quote tracking system
- Quote history for customers
- Automatic quote expiration dates
- Related product suggestions with pricing
- Bulk quote requests for multiple items
