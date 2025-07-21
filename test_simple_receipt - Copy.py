#!/usr/bin/env python3
"""Test script for the new simple receipt format"""

import sqlite3
import sys
import os
from datetime import datetime

# Add the current directory to path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import generate_pdf_receipt

def test_simple_receipt():
    """Test the new simple receipt format"""
    print("Testing simple receipt format...")
    
    # Sample tourist data for testing
    sample_data = {
        'full_name': 'John Doe',
        'father_spouse_name': 'Robert Doe',
        'mobile_number': '9876543210',
        'address': '123 Main Street, New Delhi',
        'aadhar_number': '1234-5678-9012',
        'recipe_number': 'AG20241223001',
        'amount_paid_today': '1500.00',
        'remaining_amount': '500.00',
        'male_count': 2,
        'female_count': 1,
        'children_count': 1,
        'extra_bed': True,
        'check_out_date': '25-12-2024',
        'payment_mode': 'Cash',
        'check_in_done': True
    }
    
    try:
        # Generate the receipt
        receipt_path = generate_pdf_receipt(sample_data, "101")
        
        if os.path.exists(receipt_path):
            print(f"✅ Simple receipt generated successfully: {receipt_path}")
            print(f"   File size: {os.path.getsize(receipt_path)} bytes")
            
            # Check if we can read some basic info about the PDF
            with open(receipt_path, 'rb') as f:
                content = f.read(100)  # Read first 100 bytes
                if b'PDF' in content:
                    print("   ✅ Valid PDF format detected")
                else:
                    print("   ⚠️  Warning: PDF format might be invalid")
            
            return True
        else:
            print("❌ Receipt file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error generating receipt: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("SIMPLE RECEIPT FORMAT TEST")
    print("=" * 50)
    
    success = test_simple_receipt()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed! Simple receipt format is working.")
    else:
        print("❌ Tests failed. Please check the implementation.")
    print("=" * 50)

if __name__ == "__main__":
    main()
