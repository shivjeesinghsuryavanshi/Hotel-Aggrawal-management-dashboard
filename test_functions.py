#!/usr/bin/env python3
"""
Test script to verify the hotel management system functions work correctly
after removing area, pincode, and email fields.
"""

import sqlite3
import sys
import os

# Add the current directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_schema():
    """Test that the database schema is correct"""
    print("Testing database schema...")
    
    try:
        conn = sqlite3.connect('hotel_management.db')
        cursor = conn.cursor()
        
        # Check the current schema
        cursor.execute("PRAGMA table_info(tourists)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        # Check that removed fields are not present
        forbidden_fields = ['area', 'pincode', 'email']
        for field in forbidden_fields:
            if field in columns:
                print(f"❌ ERROR: Field '{field}' should not be in schema but is present!")
                return False
        
        # Check that required fields are present
        required_fields = ['full_name', 'address', 'mobile_number', 'aadhar_number']
        for field in required_fields:
            if field not in columns:
                print(f"❌ ERROR: Required field '{field}' is missing from schema!")
                return False
        
        print("✅ Database schema is correct")
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database schema test failed: {e}")
        return False

def test_basic_queries():
    """Test basic database queries"""
    print("\nTesting basic database queries...")
    
    try:
        conn = sqlite3.connect('hotel_management.db')
        cursor = conn.cursor()
        
        # Test SELECT query
        cursor.execute("SELECT COUNT(*) FROM tourists")
        count = cursor.fetchone()[0]
        print(f"✅ Found {count} tourist records")
        
        # Test SELECT with specific fields
        cursor.execute("""
            SELECT full_name, address, mobile_number, aadhar_number, amount_paid_today, 
                   remaining_amount, room_number, check_in_date
            FROM tourists LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            print(f"✅ Sample record: {result[0]} in room {result[6]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Basic query test failed: {e}")
        return False

def test_validation_functions():
    """Test validation functions"""
    print("\nTesting validation functions...")
    
    try:
        from app import validate_form_data
        
        # Test valid data
        valid_data = {
            'full_name': 'John Doe',
            'address': '123 Main St',
            'mobile_number': '9876543210',
            'aadhar_number': '123456789012',
            'amount_paid_today': '1000',
            'remaining_amount': '500'
        }
        
        errors = validate_form_data(valid_data)
        if errors:
            print(f"❌ Validation test failed: {errors}")
            return False
        
        print("✅ Validation functions work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Hotel Management System after field removal...")
    print("=" * 60)
    
    tests = [
        test_database_schema,
        test_basic_queries,
        test_validation_functions
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The system should work correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
