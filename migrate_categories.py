#!/usr/bin/env python3
"""
Migration script to initialize the Category model and migrate from string-based categories to ID-based categories.
"""

import os
import sys

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Category, Service

def migrate_categories():
    """Migrate categories from hardcoded list to database."""
    app = create_app()
    
    with app.app_context():
        print("Starting category migration...")
        
        # Create new tables
        print("Creating Category table...")
        db.create_all()
        
        # Check if categories already exist
        existing_count = Category.query.count()
        if existing_count > 0:
            print("[OK] Categories already exist ({} found). Skipping creation.".format(existing_count))
            return
        
        # Define default categories
        default_categories = [
            {
                'name': 'Industrial Design',
                'slug': 'industrial-design',
                'description': 'Custom industrial design services',
                'order': 0
            },
            {
                'name': '3D Printing',
                'slug': '3d-printing',
                'description': 'High-quality 3D printing services',
                'order': 1
            },
            {
                'name': 'Laser Engraving',
                'slug': 'laser-engraving',
                'description': 'Precision laser engraving services',
                'order': 2
            }
        ]
        
        # Create root categories
        created_categories = {}
        print("\nCreating root categories...")
        for cat_data in default_categories:
            category = Category(
                name=cat_data['name'],
                slug=cat_data['slug'],
                description=cat_data['description'],
                order=cat_data['order'],
                parent_id=None,
                is_active=True
            )
            db.session.add(category)
            db.session.flush()  # Get the ID before commit
            created_categories[cat_data['slug']] = category
            print("  [+] Created: {} (ID: {})".format(category.name, category.id))
        
        db.session.commit()
        
        # Create some example sub-categories
        print("\nCreating example sub-categories...")
        sub_categories = [
            {
                'parent_slug': 'industrial-design',
                'name': 'CAD Design',
                'slug': 'cad-design',
                'order': 0
            },
            {
                'parent_slug': 'industrial-design',
                'name': 'Rendering',
                'slug': 'rendering',
                'order': 1
            },
            {
                'parent_slug': '3d-printing',
                'name': 'Resin',
                'slug': 'resin-printing',
                'order': 0
            },
            {
                'parent_slug': '3d-printing',
                'name': 'Filament',
                'slug': 'filament-printing',
                'order': 1
            }
        ]
        
        for sub_data in sub_categories:
            parent_cat = created_categories.get(sub_data['parent_slug'])
            if parent_cat:
                sub_category = Category(
                    name=sub_data['name'],
                    slug=sub_data['slug'],
                    description='',
                    order=sub_data['order'],
                    parent_id=parent_cat.id,
                    is_active=True
                )
                db.session.add(sub_category)
                db.session.flush()
                print("  [+] Created: {} under {} (ID: {})".format(sub_category.name, parent_cat.name, sub_category.id))
        
        db.session.commit()
        
        # Migrate existing items
        print("\nMigrating existing items...")
        items_migrated = 0
        
        # Map old category strings to new IDs
        category_map = {
            'industrial_design': created_categories['industrial-design'].id,
            '3d_printing': created_categories['3d-printing'].id,
            'laser_engraving': created_categories['laser-engraving'].id
        }
        
        # Get items that still use the old 'category' field
        try:
            # Try to migrate items with old category string
            services = Service.query.all()
            for service in services:
                # Check if the item has a category_id (new field)
                if service.category_id is None:
                    # This is an old-style item with just 'category' field
                    # Try to map it to the new category_id
                    old_category = getattr(service, 'category', None)
                    if old_category and old_category in category_map:
                        service.category_id = category_map[old_category]
                        items_migrated += 1
            
            if items_migrated > 0:
                db.session.commit()
                print("  [+] Migrated {} items to use new category hierarchy".format(items_migrated))
            else:
                print("  [OK] No legacy items to migrate")
        
        except Exception as e:
            print("  [!] Could not migrate legacy items: {}".format(e))
            print("  (This is OK if you don't have any existing items)")
        
        print("\n" + "="*50)
        print("[SUCCESS] Category migration completed successfully!")
        print("="*50)
        print("\nCreated categories:")
        for slug, cat in created_categories.items():
            print("  * {} (ID: {})".format(cat.name, cat.id))
        print("\nYou can now manage categories at: /admin/categories")

if __name__ == '__main__':
    migrate_categories()
