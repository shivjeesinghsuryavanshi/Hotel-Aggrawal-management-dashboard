#!/usr/bin/env python3
"""
Test script for receipt system fixes
"""

import sys
sys.path.append('.')

from receipt_system import generate_receipt_with_number, get_tourist_full_data, generate_custom_hindi_receipt

def test_receipt_generation():
    print("Testing receipt generation...")
    
    # Test with tourist ID 1 (from schema check we know this exists)
    tourist_id = 1
    
    # Generate receipt number
    receipt_number, message = generate_receipt_with_number(tourist_id)
    print(f"Receipt generation result: {receipt_number}, Message: {message}")
    
    if receipt_number:
        # Get full tourist data
        tourist_data = get_tourist_full_data(tourist_id)
        if tourist_data:
            print(f"Tourist data retrieved: {tourist_data['full_name']}")
            print(f"Current recipe number: {tourist_data.get('recipe_number', 'None')}")
            
            # Generate PDF receipt
            try:
                pdf_path = generate_custom_hindi_receipt(tourist_data, receipt_number)
                print(f"PDF generated successfully at: {pdf_path}")
                return True
            except Exception as e:
                print(f"Error generating PDF: {e}")
                return False
        else:
            print("Could not retrieve tourist data")
            return False
    else:
        print("Could not generate receipt number")
        return False

if __name__ == "__main__":
    success = test_receipt_generation()
    if success:
        print("✅ Receipt system test passed!")
    else:
        print("❌ Receipt system test failed!")
