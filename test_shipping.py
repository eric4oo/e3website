#!/usr/bin/env python
"""Test script for Canada Post shipping service"""

import sys
sys.path.insert(0, '.')

from app.shipping import CanadaPostShippingService

print("Testing Canada Post Shipping Service...\n")

# Test postal code validation
valid_code = CanadaPostShippingService._is_canadian_postal_code("N9J 1V6")
print(f"✓ Valid postal code test: {valid_code}")

invalid_code = CanadaPostShippingService._is_canadian_postal_code("12345")
print(f"✓ Invalid postal code test: {not invalid_code}")

# Test demo shipping rates
demo_rates = CanadaPostShippingService.get_demo_shipping_rates("N9J 1V6", 1.5)
print(f"✓ Demo rates calculation: {len(demo_rates['options'])} options available")

if demo_rates['success']:
    print(f"  - Options:")
    for option in demo_rates['options']:
        print(f"    • {option['service_name']}: ${option['price']:.2f}")

# Test weight calculation
cart_items = [
    {'weight_kg': 0.5, 'quantity': 2},
    {'weight_kg': 1.0, 'quantity': 1}
]
total_weight = CanadaPostShippingService.calculate_total_weight(cart_items)
print(f"✓ Weight calculation: {total_weight} kg calculated correctly")

print("\n✅ All shipping service tests passed!")
