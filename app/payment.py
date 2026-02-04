"""
Square Payment Integration Module
Handles all Square payment processing for the e-commerce platform
"""

from square import Square
from flask import current_app
import uuid
import logging

logger = logging.getLogger(__name__)


class SquarePaymentProcessor:
    """Handles Square payment processing."""
    
    def __init__(self):
        """Initialize Square client with app configuration."""
        access_token = current_app.config.get('SQUARE_ACCESS_TOKEN')
        environment = current_app.config.get('SQUARE_ENVIRONMENT', 'sandbox')
        
        # Create Square SDK client
        self.client = Square(
            access_token=access_token,
            environment=environment
        )
    
    def process_payment(self, amount_cents, source_id, idempotency_key=None):
        """
        Process a payment through Square.
        
        Args:
            amount_cents (int): Amount in cents
            source_id (str): Source ID from Square Web Payments SDK (nonce)
            idempotency_key (str): Unique key for idempotency (optional)
        
        Returns:
            dict: Payment result with payment ID or error details
        """
        try:
            if not idempotency_key:
                idempotency_key = str(uuid.uuid4())
            
            # Create payment body
            payment_body = {
                'source_id': source_id,
                'amount_money': {
                    'amount': amount_cents,
                    'currency': 'USD'
                },
                'idempotency_key': idempotency_key
            }
            
            # Call Square API
            result = self.client.payments.create_payment(payment_body)
            
            if result.is_success():
                payment = result.result.payment
                return {
                    'success': True,
                    'payment_id': payment.id,
                    'status': payment.status,
                    'amount': payment.amount_money.amount,
                    'receipt_url': getattr(payment, 'receipt_url', None)
                }
            elif result.is_client_error():
                logger.error(f"Client error: {result.errors}")
                return {
                    'success': False,
                    'error': 'Invalid payment information',
                    'details': result.errors
                }
            else:
                logger.error(f"Server error: {result.errors}")
                return {
                    'success': False,
                    'error': 'Payment processing error',
                    'details': result.errors
                }
        
        except Exception as e:
            logger.error(f"Exception during payment processing: {str(e)}")
            return {
                'success': False,
                'error': 'Payment processing failed',
                'details': str(e)
            }
    
    def refund_payment(self, payment_id, amount_cents=None):
        """
        Refund a Square payment.
        
        Args:
            payment_id (str): Square payment ID
            amount_cents (int): Amount to refund in cents (optional, full refund if not provided)
        
        Returns:
            dict: Refund result
        """
        try:
            refund_body = {
                'idempotency_key': str(uuid.uuid4())
            }
            
            if amount_cents:
                refund_body['amount_money'] = {
                    'amount': amount_cents,
                    'currency': 'USD'
                }
            
            result = self.client.refunds.refund_payment(payment_id, refund_body)
            
            if result.is_success():
                refund = result.result.refund
                return {
                    'success': True,
                    'refund_id': refund.id,
                    'status': refund.status,
                    'amount': refund.amount_money.amount
                }
            else:
                logger.error(f"Refund error: {result.errors}")
                return {
                    'success': False,
                    'error': 'Refund failed',
                    'details': result.errors
                }
        
        except Exception as e:
            logger.error(f"Exception during refund: {str(e)}")
            return {
                'success': False,
                'error': 'Refund processing failed',
                'details': str(e)
            }
    
    def get_payment(self, payment_id):
        """
        Retrieve payment details from Square.
        
        Args:
            payment_id (str): Square payment ID
        
        Returns:
            dict: Payment details
        """
        try:
            result = self.client.payments.retrieve_payment(payment_id)
            
            if result.is_success():
                payment = result.result.payment
                return {
                    'success': True,
                    'payment_id': payment.id,
                    'status': payment.status,
                    'amount': payment.amount_money.amount,
                    'receipt_url': getattr(payment, 'receipt_url', None)
                }
            else:
                logger.error(f"Get payment error: {result.errors}")
                return {
                    'success': False,
                    'error': 'Could not retrieve payment',
                    'details': result.errors
                }
        
        except Exception as e:
            logger.error(f"Exception retrieving payment: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to retrieve payment',
                'details': str(e)
            }


def get_square_processor():
    """Factory function to get Square payment processor."""
    return SquarePaymentProcessor()
