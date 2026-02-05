# PropsWorks Admin Panel - Content Management System

## Overview

The PropsWorks Admin Panel is a powerful content management system that allows you to edit and manage all text instances and design elements of your website without touching code.

## Access the Admin Panel

1. **Start the Flask server**:
   ```bash
   python -m flask run --port 5000
   ```

2. **Navigate to admin login**:
   ```
   http://localhost:5000/admin/login
   ```

3. **Enter the admin password**:
   - Default: `admin123`
   - Change via `.env` file: `ADMIN_PASSWORD=your_secure_password`

## Features

### 1. General Content Tab
- **Site Information**: Edit site title and tagline
- **Hero Section**: Customize hero title and subtitle
- **About Section**: Manage about page title and content

### 2. Services Tab
- Edit service titles, descriptions, and prices
- Services include:
  - Industrial Design
  - 3D Printing
  - Laser Engraving
- Changes are instantly saved to the database

### 3. Design Tab
- **Color Scheme Management**:
  - Primary Color (brand color)
  - Secondary Color (accent color)
  - Accent Color (highlights)
  - Background Color
  - Text Color
- Visual color picker with hex input
- Live preview of colors

### 4. Contact Tab
- Email address
- Phone number
- Manage contact information

## Live Preview

The admin panel includes a **live preview panel** on the right side that shows:
- Real-time updates of all edited content
- Color scheme visualization
- Site information preview

## How to Use

### Editing Text Content

1. Click on the desired tab (General, Services, Design, Contact)
2. Edit the text fields
3. See changes reflected in the live preview
4. Click **"Save All"** button to persist changes

### Changing Colors

1. Go to the **Design** tab
2. Click the color square to open the color picker
3. Or enter hex codes directly in the text field
4. Colors update in real-time in the preview

### Managing Services

1. Go to the **Services** tab
2. Update title, description, and price for each service
3. Changes are saved when you click **"Save All"**

## File Structure

```
app/admin.py                          # Admin routes and API endpoints
templates/admin/
  ├── login.html                      # Login page
  └── dashboard.html                  # Main admin interface
instance/content.json                 # Content storage (auto-created)
```

## API Endpoints

All endpoints require admin authentication via session.

### Get All Content
```
GET /admin/api/content
Response: JSON with all site content
```

### Save All Content
```
POST /admin/api/content
Body: JSON with updated content
Response: { "success": true/false }
```

### Update Specific Item
```
PUT /admin/api/content/<key>
Body: { "value": "new_value" }
Response: { "success": true/false }
```

### Update Service
```
PUT /admin/api/content/service/<service_id>
Body: JSON with service updates
Response: { "success": true/false }
```

## Content Storage

Content is stored in `instance/content.json` with the following structure:

```json
{
  "site_title": "PropsWorks",
  "site_tagline": "Custom Props & Manufacturing",
  "hero_title": "Welcome to PropsWorks",
  "hero_subtitle": "Professional Props and Manufacturing",
  "about_title": "About PropsWorks",
  "about_content": "...",
  "services": {
    "industrial_design": {
      "title": "...",
      "description": "...",
      "price": 5000
    },
    ...
  },
  "colors": {
    "primary": "#2c3e50",
    "secondary": "#3498db",
    "accent": "#e74c3c",
    "background": "#ecf0f1",
    "text": "#2c3e50"
  },
  "contact_email": "info@propsworks.com",
  "contact_phone": "(555) 123-4567",
  "last_updated": "2026-02-05T10:30:00.000000"
}
```

## Security

### Password Protection
- Admin panel requires password authentication
- Change default password in `.env`:
  ```
  ADMIN_PASSWORD=your_very_secure_password
  ```

### Session Management
- Sessions are HTTP-only cookies
- Sessions expire after 7 days of inactivity
- Logout clears session data

### In Production
For production deployments:
1. Use strong ADMIN_PASSWORD
2. Set `SESSION_COOKIE_SECURE=True` (HTTPS only)
3. Use environment-based authentication
4. Consider implementing OAuth/SSO

## Extending the Admin Panel

### Adding New Content Fields

1. **Update `app/admin.py`**:
   - Add default value in `init_content_file()`
   - Create API endpoint if needed

2. **Update `dashboard.html`**:
   - Add form input in appropriate tab
   - Add JavaScript listener with `addChangeListeners()`
   - Update `saveAllContent()` to include new field

3. **Test the changes**:
   - Login to admin panel
   - Verify new field appears
   - Save and check `instance/content.json`

### Example: Adding a New Field

```javascript
// In dashboard.html, add to form:
<div class="form-group">
    <label>My New Field</label>
    <input type="text" id="my_new_field">
</div>

// In saveAllContent():
my_new_field: document.getElementById('my_new_field').value,

// In populateForm():
document.getElementById('my_new_field').value = contentData.my_new_field || '';
```

## Troubleshooting

### Admin panel not loading
- Ensure Flask server is running
- Check that `.venv` is activated
- Verify no port conflicts on 5000

### Content not saving
- Check browser console for JavaScript errors
- Verify `instance/` directory exists
- Check file permissions on `instance/content.json`

### Session expires quickly
- Adjust `PERMANENT_SESSION_LIFETIME` in `config.py`
- Default is 7 days

### Password not working
- Make sure you're using the correct password
- Check `.env` file for `ADMIN_PASSWORD` override
- Default is `admin123`

## Support

For issues or feature requests, contact the development team or check the main README.md.
