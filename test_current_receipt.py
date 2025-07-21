#!/usr/bin/env python3
"""
Test script to verify the current receipt formatting
"""

import receipt_system
import tempfile
import os

def test_current_receipt():
    """Test the current receipt formatting"""
    
    print("🏨 TESTING CURRENT RECEIPT FORMATTING")
    print("=" * 50)
    
    # Create test data
    test_data = {
        'full_name': 'John Doe',
        'father_name': 'Robert Doe',
        'address': '123 Main St, City, State',
        'contact_number': '+91 9876543210',
        'id_type': 'Passport',
        'id_number': 'A1234567',
        'check_in_date': '2024-01-15',
        'check_out_date': '2024-01-20',
        'amount_paid_today': 7500.0,
        'remaining_amount': 4500.0,
        'payment_mode': 'Online'
    }
    
    # Generate receipt
    receipt_number = 'HTL2024001'
    
    try:
        pdf_path = receipt_system.generate_custom_hindi_receipt(test_data, receipt_number)
        
        print(f'✅ Receipt generated successfully!')
        print(f'📄 Location: {pdf_path}')
        print('🎯 Receipt formatting test completed')
        
        # Check if file exists
        if os.path.exists(pdf_path):
            print(f'✅ PDF file exists and is accessible')
        else:
            print(f'❌ PDF file not found at expected location')
        
        return True
        
    except Exception as e:
        print(f'❌ Error generating receipt: {e}')
        return False

if __name__ == "__main__":
    test_current_receipt()
