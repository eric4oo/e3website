"""
Canada Post Real-Time Shipping Integration Service

This module handles communication with the Canada Post API to:
- Calculate real-time shipping rates for different services
- Get available shipping methods based on origin and destination
- Support all Canada Post domestic and international services
"""

import os
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

import xml.etree.ElementTree as ET
from decimal import Decimal
from typing import List, Dict, Optional, Tuple


class CanadaPostShippingService:
    """
    Handles real-time shipping rate calculation via Canada Post API.
    
    Services supported:
    - DOM.RP: Regular Parcel (Domestic)
    - DOM.EP: Express (Domestic)
    - DOM.XP: Xpresspost (Domestic)
    - DOM.PRIORITY: Priority (Domestic)
    - INTL.IP: International Parcel
    - INTL.PW: Priority Worldwide (XPress)
    - INTL.XIP: Xpresspost International
    """
    
    API_ENDPOINT = "https://ct.canadapost.ca/getnrates"
    USERNAME = os.environ.get('CANADA_POST_USERNAME', '')
    PASSWORD = os.environ.get('CANADA_POST_PASSWORD', '')
    CUSTOMER_NUMBER = os.environ.get('CANADA_POST_CUSTOMER_NUMBER', '')
    
    # Origin postal code (where packages ship from)
    ORIGIN_POSTAL_CODE = "N9J1V6"  # User's location
    
    # Service codes and display names (all services - user can filter)
    DOMESTIC_SERVICES = {
        'DOM.RP': 'Regular Parcel',
        'DOM.EP': 'Express',
        'DOM.XP': 'Xpresspost',
        'DOM.PRIORITY': 'Priority'
    }
    
    INTERNATIONAL_SERVICES = {
        'INTL.IP': 'International Parcel',
        'INTL.PW': 'Priority Worldwide (Xpress)',
        'INTL.XIP': 'Xpresspost International'
    }
    
    # Canada Post service codes for filtering
    ENABLED_DOMESTIC = {'DOM.RP', 'DOM.EP', 'DOM.XP', 'DOM.PRIORITY'}
    ENABLED_INTERNATIONAL = {'INTL.IP', 'INTL.PW', 'INTL.XIP'}
    
    @classmethod
    def _get_auth(cls) -> Tuple[str, str]:
        """Get authentication tuple for Canada Post API."""
        if not cls.USERNAME or not cls.PASSWORD:
            raise ValueError(
                "Canada Post API credentials not configured. "
                "Set CANADA_POST_USERNAME and CANADA_POST_PASSWORD environment variables."
            )
        return (cls.USERNAME, cls.PASSWORD)
    
    @classmethod
    def _is_canadian_postal_code(cls, postal_code: str) -> bool:
        """Check if postal code is Canadian format (A1A 1A1)."""
        postal_code = postal_code.strip().upper().replace(' ', '')
        return (
            len(postal_code) == 6 and
            postal_code[0].isalpha() and
            postal_code[1].isdigit() and
            postal_code[2].isalpha() and
            postal_code[3].isdigit() and
            postal_code[4].isalpha() and
            postal_code[5].isdigit()
        )
    
    @classmethod
    def _parse_api_response(cls, xml_response: str) -> List[Dict]:
        """
        Parse Canada Post API XML response into list of shipping options.
        
        Returns list of dicts with:
        {
            'service_code': 'DOM.RP',
            'service_name': 'Regular Parcel',
            'price': 12.99,
            'guaranteed_days': '3-5',
            'est_delivery_date': '2026-02-10'
        }
        """
        options = []
        try:
            root = ET.fromstring(xml_response)
            
            # Handle error responses
            if root.tag == 'error':
                error_msg = root.find('message')
                details = root.find('detail')
                if error_msg is not None:
                    raise ValueError(f"Canada Post API Error: {error_msg.text}")
                if details is not None:
                    raise ValueError(f"Canada Post API Error: {details.text}")
                raise ValueError("Canada Post API returned an error")
            
            # Parse rates
            for service in root.findall('service'):
                service_code = service.find('service-code')
                service_name = service.find('service-name')
                price = service.find('price')
                guaranteed_days = service.find('guaranteed-days')
                est_delivery_date = service.find('est-delivery-date')
                
                if service_code is not None and price is not None:
                    options.append({
                        'service_code': service_code.text or '',
                        'service_name': service_name.text if service_name is not None else 'Unknown',
                        'price': float(price.text or '0'),
                        'guaranteed_days': guaranteed_days.text if guaranteed_days is not None else 'N/A',
                        'est_delivery_date': est_delivery_date.text if est_delivery_date is not None else 'N/A'
                    })
        
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse Canada Post API response: {str(e)}")
        
        return options
    
    @classmethod
    def get_shipping_rates(
        cls,
        destination_postal_code: str,
        weight_kg: float,
        domestic_only: bool = True
    ) -> Dict[str, any]:
        """
        Get real-time shipping rates from Canada Post API.
        
        Args:
            destination_postal_code: Customer's postal code
            weight_kg: Total weight of package in kilograms
            domestic_only: Only get domestic rates if True
        
        Returns dictionary:
        {
            'success': True/False,
            'error': None or error message,
            'origin': 'N9J 1V6',
            'destination': postal_code,
            'weight_kg': weight_kg,
            'options': [
                {
                    'service_code': 'DOM.RP',
                    'service_name': 'Regular Parcel',
                    'price': 12.99,
                    'guaranteed_days': '3-5'
                },
                ...
            ]
        }
        """
        result = {
            'success': False,
            'error': None,
            'origin': cls.ORIGIN_POSTAL_CODE,
            'destination': destination_postal_code,
            'weight_kg': weight_kg,
            'options': []
        }
        
        # Validate inputs
        if not cls._is_canadian_postal_code(destination_postal_code):
            result['error'] = 'Invalid Canadian postal code format (e.g., N9J 1V6)'
            return result
        
        if weight_kg <= 0:
            result['error'] = 'Weight must be greater than 0 kg'
            return result
        
        if weight_kg > 30:
            result['error'] = 'Weight exceeds 30 kg maximum for parcels'
            return result
        
        # Check API credentials
        if not cls.USERNAME or not cls.PASSWORD:
            result['error'] = (
                'Canada Post API credentials not configured. '
                'Please contact support or configure the shipping service.'
            )
            return result
        
        try:
            # Build request XML
            destination_postal_code_formatted = destination_postal_code.strip().upper().replace(' ', '')
            
            # Weight must be in grams for API (convert from kg)
            weight_grams = int(weight_kg * 1000)
            
            # Check if requests library is available
            if not HAS_REQUESTS:
                result['error'] = 'requests library not installed. Using demo rates instead.'
                # Fall back to demo rates
                demo_result = cls.get_demo_shipping_rates(destination_postal_code, weight_kg)
                demo_result['is_demo'] = True
                return demo_result
            
            # Build rate request XML
            request_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
            <eparcel>
                <quote>
                    <origin-postal-code>{cls.ORIGIN_POSTAL_CODE}</origin-postal-code>
                    <destination-postal-code>{destination_postal_code_formatted}</destination-postal-code>
                    <parcel>
                        <weight>{weight_grams}</weight>
                    </parcel>
                </quote>
            </eparcel>'''
            
            # Make API request
            response = requests.post(
                cls.API_ENDPOINT,
                auth=cls._get_auth(),
                data=request_xml,
                headers={'Content-Type': 'application/xml'},
                timeout=10
            )
            
            response.raise_for_status()
            
            # Parse response
            options = cls._parse_api_response(response.text)
            
            # Filter based on domestic_only flag
            if domestic_only:
                options = [o for o in options if o['service_code'] in cls.ENABLED_DOMESTIC]
            else:
                # Filter to enabled services
                enabled = cls.ENABLED_DOMESTIC | cls.ENABLED_INTERNATIONAL
                options = [o for o in options if o['service_code'] in enabled]
            
            # Sort by price (cheapest first)
            options = sorted(options, key=lambda x: x['price'])
            
            result['success'] = True
            result['options'] = options
            
        except requests.exceptions.RequestException as e:
            result['error'] = f'Failed to connect to Canada Post service: {str(e)}'
        except ValueError as e:
            result['error'] = str(e)
        except Exception as e:
            result['error'] = f'Unexpected error: {str(e)}'
        
        return result
    
    @classmethod
    def get_demo_shipping_rates(
        cls,
        destination_postal_code: str,
        weight_kg: float
    ) -> Dict[str, any]:
        """
        Get demo shipping rates for testing without API credentials.
        Uses realistic estimates based on Canada Post standard rates.
        """
        result = {
            'success': True,
            'error': None,
            'origin': cls.ORIGIN_POSTAL_CODE,
            'destination': destination_postal_code,
            'weight_kg': weight_kg,
            'options': [
                {
                    'service_code': 'DOM.RP',
                    'service_name': 'Regular Parcel',
                    'price': round(8.95 + (weight_kg * 0.5), 2),
                    'guaranteed_days': '3-5',
                    'est_delivery_date': 'Approximately 3-5 business days'
                },
                {
                    'service_code': 'DOM.EP',
                    'service_name': 'Express',
                    'price': round(16.45 + (weight_kg * 1.0), 2),
                    'guaranteed_days': '1-2',
                    'est_delivery_date': 'Next business day to 2 business days'
                },
                {
                    'service_code': 'DOM.XP',
                    'service_name': 'Xpresspost',
                    'price': round(24.95 + (weight_kg * 1.5), 2),
                    'guaranteed_days': '1',
                    'est_delivery_date': 'Next business day'
                },
                {
                    'service_code': 'DOM.PRIORITY',
                    'service_name': 'Priority',
                    'price': round(35.95 + (weight_kg * 2.0), 2),
                    'guaranteed_days': 'Overnight',
                    'est_delivery_date': 'Next business day'
                }
            ]
        }
        
        # Sort by price
        result['options'] = sorted(result['options'], key=lambda x: x['price'])
        return result
    
    @classmethod
    def calculate_total_weight(cls, cart_items: List[Dict]) -> float:
        """
        Calculate total weight of cart items.
        
        Args:
            cart_items: List of cart item dicts with 'weight_kg' and 'quantity' fields
        
        Returns: Total weight in kilograms
        """
        total_weight = 0
        for item in cart_items:
            weight = item.get('weight_kg', 0.5)  # Default 0.5kg if not specified
            quantity = item.get('quantity', 1)
            total_weight += weight * quantity
        
        return max(total_weight, 0.5)  # Minimum 0.5kg (Canada Post minimum)
