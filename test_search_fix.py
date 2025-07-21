#!/usr/bin/env python3
"""
Test script for search functionality
"""

import sys
sys.path.append('.')

from receipt_system import search_tourists

def test_search_functionality():
    print("Testing search functionality...")
    
    # Test basic search
    results, error = search_tourists()
    if error:
        print(f"Error in basic search: {error}")
        return False
    
    print(f"Found {len(results)} tourists in basic search")
    
    # Test receipt filter
    results_with_receipt, error = search_tourists(receipt_filter="yes")
    if error:
        print(f"Error in receipt filter search: {error}")
        return False
    
    print(f"Found {len(results_with_receipt)} tourists with receipts")
    
    # Test name search
    results_name, error = search_tourists(search_term="Shiv")
    if error:
        print(f"Error in name search: {error}")
        return False
    
    print(f"Found {len(results_name)} tourists matching 'Shiv'")
    
    # Print sample result
    if results:
        sample = results[0]
        print(f"Sample tourist: {sample['full_name']}")
        print(f"Receipt number: {sample.get('receipt_number', 'None')}")
        print(f"Receipt generated: {sample.get('receipt_generated', False)}")
    
    return True

if __name__ == "__main__":
    success = test_search_functionality()
    if success:
        print("✅ Search functionality test passed!")
    else:
        print("❌ Search functionality test failed!")
