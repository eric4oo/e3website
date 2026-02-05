# Item Management Guide

This guide explains how to use the new Item Management system in the PropsWorks admin panel.

## Overview

The Item Management interface allows you to:
- **Add new items/services** with full details
- **Edit existing items** and their properties
- **Manage pricing** including bulk discount tiers
- **Upload media** (photos and videos) for each item
- **Organize items** by category
- **Toggle items active/inactive** for visibility on the website

## Accessing Item Management

1. Log in to the admin panel at `/admin/login`
2. Click the **"Manage Items"** button at the top of the Content Editor dashboard
3. Or navigate directly to `/admin/items`

## Managing Items

### Viewing Items

When you first load the Item Management page, you'll see:
- **All items** from all categories
- **Category filters** at the top to view items by category
- **Item cards** displaying:
  - Item thumbnail image
  - Item name and category
  - Description (first 2 lines)
  - Base price
  - Count of media files and pricing tiers
  - Edit and Delete buttons

### Adding a New Item

1. Click the **"Add New Item"** button (top right)
2. A form will open with the following sections:

#### Basic Information
- **Item Name*** - The display name of the service/product
- **Category*** - Choose from:
  - Industrial Design
  - 3D Printing
  - Laser Engraving
- **Short Description*** - Brief 1-2 sentence description
- **Long Description** - Detailed description, specifications, features (optional)

#### Pricing
- **Contact for Quote** - Check this if you want customers to contact you for pricing instead of adding to cart
- **Base Price ($)** - The standard price for this item (leave empty if using Contact for Quote)
- **Image URL** - Link to the main product/service image

**When to Use "Contact for Quote":**
- Custom projects with pricing that varies by specifications
- Enterprise/bulk orders that need custom quotes
- Services that require consultation before pricing
- Limited-edition or made-to-order items

#### Bulk Pricing Tiers (Optional)
Configure reduced pricing for large orders:

1. Click **"Add Pricing Tier"** button
2. For each tier, specify:
   - **Min Quantity** - Minimum order quantity for this price to apply
   - **Price ($)** - The reduced price per item at this quantity

**Example:**
```
Tier 1: Min Quantity: 10, Price: $450 (instead of $500)
Tier 2: Min Quantity: 25, Price: $400
Tier 3: Min Quantity: 50, Price: $350
```

When a customer orders 10+ items, they automatically get the $450 price.
When ordering 25+, they get $400, etc.

**Note:** Bulk pricing is not available for items using "Contact for Quote"

#### Product Variants (Optional)
Add different versions of the same product with separate pricing:

1. Click **"Add Variant"** button
2. For each variant, specify:
   - **Variant Name*** - The version identifier (e.g., "Small", "Large", "Red", "Blue")
   - **Contact for Quote** - Optionally check this for individual variants (different from base item)
   - **Price ($)** - The price for this specific variant (leave empty if using Contact for Quote)
   - **Description/Notes** - Optional details about this variant (dimensions, materials, colors, etc.)
   - **SKU/Item Code** - Optional inventory tracking identifier
   - **Available for purchase** - Checkbox to enable/disable this variant

**Example - T-Shirt Product:**
```
Variant 1: Small - $25 - Description: Fits XS-S
Variant 2: Medium - $25 - Description: Fits M-L  
Variant 3: Large - $27 - Description: Fits XL-XXL
Variant 4: Extra Large - Contact for Quote - Custom sizing available
```

**Example - Custom Brackets:**
```
Variant 1: Steel - $150 - Description: Powder coated steel, 5 day turnaround
Variant 2: Aluminum - $120 - Description: Anodized aluminum, 3 day turnaround
Variant 3: Stainless Steel - Contact for Quote - Food grade, custom specifications
```

**When to Use Variants:**
- Different sizes of the same item (may have different prices)
- Different colors available (may have different prices)
- Different materials with different costs
- Mix of standard options and custom/quote options
Upload photos and videos to showcase your items:

1. Click the upload area or drag & drop files
2. Supported formats:
   - **Photos:** PNG, JPG, JPEG, GIF, WEBP
   - **Videos:** MP4, WEBM, MOV, AVI
3. Add an optional **Caption** for the media
4. Click **"Upload Media"** button
5. The media will appear in the gallery below

**Important:** You must save the item first before uploading media files.

#### Status
- Check **"Active (visible on website)"** to display this item on your site
- Uncheck to hide the item from customers

### Editing Items

1. Find the item in the grid and click the **"Edit"** button
2. Modify any fields as needed
3. Add/remove bulk pricing tiers
4. Add new media or delete existing media
5. Click **"Save Item"** to apply changes

**To delete media:**
- Hover over a media file in the gallery
- Click the **"Delete"** button that appears

### Deleting Items

1. Click the **"Delete"** button on an item card
2. Confirm the deletion when prompted
3. The item and all its media will be permanently deleted

## Pricing Logic

### How Bulk Pricing Works

When a customer adds items to their cart, the price is automatically calculated based on quantity:

1. **Single item to minimum threshold** - Uses base price
2. **At or above a tier's minimum** - Uses that tier's price (the highest applicable tier is used)
3. **Multiple pricing tiers** - Always applies the lowest price available for the quantity

```python
# Example pricing for an item:
Base Price: $500
Tier 1: 10+ items @ $450
Tier 2: 25+ items @ $400
Tier 3: 50+ items @ $350

Order quantities:
- 5 items: 5 × $500 = $2,500
- 10 items: 10 × $450 = $4,500
- 25 items: 25 × $400 = $10,000
- 50 items: 50 × $350 = $17,500
```

## Media Management

### Types of Media

**Photos:**
- Best for: Product images, service examples, finished results
- Formats: PNG, JPG, JPEG, GIF, WEBP
- Recommended size: 800×600px or larger
- Recommended format: JPG (compressed) or WEBP (modern, smaller)

**Videos:**
- Best for: Process videos, tutorials, showcase videos
- Formats: MP4, WEBM, MOV, AVI
- Recommended: Keep videos under 10MB for fast website loading

### Media Captions

Each media file can have a caption that displays alongside it:
- Product name or variation
- Brief description of what's shown
- Technical specifications
- Any other relevant information

### Media Organization

- Media is stored in `/static/uploads/`
- Files are automatically named with timestamps to prevent conflicts
- All media is associated with its specific item
- Deleting an item automatically removes all associated media files

## File Upload Limitations

- **Maximum file size:** Limited by server configuration (typically 16MB)
- **Allowed file types:** Only image and video formats listed above
- **Upload timeout:** May take longer for large video files

## Tips & Best Practices

### Pricing Strategy
- Start with competitive base pricing
- Consider material costs and labor
- Bulk tiers should offer 10-20% discounts
- Round prices to common amounts ($X.95, $X.99, etc.)

### Media Tips
- **Use high-quality images** - First impression matters
- **Consistent styling** - Keep a uniform look across all items
- **Show variations** - Include multiple angles or use cases
- **Update regularly** - Add new photos/videos periodically
- **Optimize file sizes** - Compress images to reduce page load time

### Description Writing
- **Short description:** 1-2 sentences, what is it?
- **Long description:** Details, specs, materials, process, timeline
- **Be clear and specific** - Avoid vague language
- **Include turnaround time** - How long does production take?
- **Highlight unique features** - What makes this special?

### Category Organization
- Use consistent categories for easy browsing
- Only create items in the predefined categories
- Ensure correct categorization for user experience

## Troubleshooting

### Media Won't Upload
1. Check file format is supported
2. Verify file size isn't too large
3. Try a different file format
4. Ensure item is saved before uploading media
5. Check browser console for error messages

### Changes Not Saving
1. Ensure all required fields are filled (marked with *)
2. Check that numbers are valid (price > 0)
3. Verify category is selected
4. Look for error message at top of form
5. Try refreshing the page and try again

### Can't See New Items on Website
1. Verify the item is **Active** (checkbox should be checked)
2. Hit F5 or Ctrl+Shift+R to clear browser cache
3. Check that category is correct
4. Verify image URL is accessible
5. Wait a few seconds for the page to sync

## Database Fields Reference

Each item stores the following information:

```json
{
  "id": 1,
  "name": "Industrial Design Service",
  "slug": "industrial-design-service",
  "description": "Custom CAD and design services",
  "long_description": "Full product design from concept to manufacturing-ready drawings...",
  "price_base": 5000,
  "category": "industrial_design",
  "image_url": "https://example.com/image.jpg",
  "is_active": true,
  "media_gallery": [
    {
      "type": "photo",
      "url": "/static/uploads/1_1704067200_example.jpg",
      "caption": "Design process visualization",
      "uploaded_at": "2024-01-01T12:00:00"
    }
  ],
  "bulk_pricing": [
    {
      "min_quantity": 10,
      "price": 450
    }
  ],
  "variants": [
    {
      "name": "Small",
      "price": 100,
      "description": "5x5 inches",
      "sku": "DESIGN-SMALL",
      "is_available": true
    },
    {
      "name": "Large",
      "price": 150,
      "description": "10x10 inches",
      "sku": "DESIGN-LARGE",
      "is_available": true
    }
  ],
  "created_at": "2024-01-01T12:00:00"
}
```

## API Endpoints

For developers, the following endpoints are available:

- `GET /admin/api/items` - List all items
- `GET /admin/api/items?category=industrial_design` - Filter by category
- `GET /admin/api/items/<id>` - Get specific item
- `POST /admin/api/items` - Create new item
- `PUT /admin/api/items/<id>` - Update item
- `DELETE /admin/api/items/<id>` - Delete item
- `POST /admin/api/items/<id>/upload-media` - Upload media file
- `DELETE /admin/api/items/<id>/media/<index>` - Delete media file

All endpoints require admin authentication (login).

## Next Steps

After setting up items:
1. Add at least one item from each category for the website
2. Include high-quality photos for each item
3. Set up bulk pricing if offering quantity discounts
4. Write detailed descriptions for each item
5. Test the items on the front-end website
6. Monitor customer interest and adjust prices as needed

## Support

For issues or questions:
1. Check this guide first
2. Review browser console for error messages
3. Check server logs for detailed errors
4. Verify database connectivity
5. Ensure Flask application is running properly
