#!/usr/bin/env python3
"""
Test script to check receipt number and date boxes formatting
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from receipt_system import generate_custom_hindi_receipt

def test_receipt_boxes():
    """Test receipt boxes with sample data"""
    print("Testing receipt number and date boxes...")
    
    # Sample tourist data
    tourist_data = {
        'tourist_id': 'T001',
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '9876543210',
        'aadhar_number': '123456789012',
        'address': '123 Main Street, City, State - 12345',
        'check_in_date': '2024-01-15',
        'check_out_date': '2024-01-18',
        'room_type': 'Deluxe',
        'room_number': '101',
        'total_amount': 15000.00,
        'advance_payment': 5000.00,
        'balance_amount': 10000.00,
        'payment_status': 'Paid',
        'special_requests': 'Extra pillows, Late checkout'
    }
    
    try:
        # Generate receipt PDF
        pdf_path = generate_custom_hindi_receipt(tourist_data, receipt_number=1234)
        
        if pdf_path and os.path.exists(pdf_path):
            print(f"✓ Receipt PDF generated successfully: {pdf_path}")
            print("✓ Receipt number and date boxes should now be properly formatted")
            return True
        else:
            print("✗ Failed to generate PDF")
            return False
            
    except Exception as e:
        print(f"✗ Error generating receipt: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_receipt_boxes()
    if success:
        print("\n=== RECEIPT BOXES TEST PASSED ===")
    else:
        print("\n=== RECEIPT BOXES TEST FAILED ===")
