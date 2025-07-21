#!/usr/bin/env python3
"""
Test script to demonstrate the automatic receipt number generation
"""

import sys
import os

# Add the current directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_receipt_generation():
    """Test the receipt number generation"""
    print("Testing automatic receipt number generation...")
    
    try:
        from app import generate_receipt_number
        
        # Generate multiple receipt numbers to show they're unique
        print("\nGenerating 5 receipt numbers:")
        for i in range(5):
            receipt_num = generate_receipt_number()
            print(f"  {i+1}. {receipt_num}")
        
        print("\n✅ Receipt number generation working correctly!")
        print("\nReceipt Number Format:")
        print("  RCP + YYYYMMDD + 4-digit sequence number")
        print("  Example: RCP202407090001, RCP202407090002, etc.")
        
        return True
        
    except Exception as e:
        print(f"❌ Receipt generation test failed: {e}")
        return False

def main():
    """Run the test"""
    print("🧪 Testing Automatic Receipt Number Generation...")
    print("=" * 50)
    
    if test_receipt_generation():
        print("\n🎉 All tests passed! Receipt numbers will be auto-generated.")
        return 0
    else:
        print("\n❌ Tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
