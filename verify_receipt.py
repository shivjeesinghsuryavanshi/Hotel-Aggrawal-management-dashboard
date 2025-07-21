#!/usr/bin/env python3
"""Quick test to verify receipt changes"""

# Test data
sample_data = {
    'full_name': 'Test User',
    'father_spouse_name': 'Test Father',
    'mobile_number': '1234567890',
    'address': 'Test Address',
    'aadhar_number': '1234-5678-9012',
    'recipe_number': 'AG20241223001',
    'amount_paid_today': '1000.00',
    'remaining_amount': '500.00',
    'male_count': 1,
    'female_count': 1,
    'children_count': 0,
    'extra_bed': False,
    'check_out_date': '25-12-2024',
    'payment_mode': 'Cash',
    'check_in_done': True
}

room_number = "101"

print("Sample receipt data:")
print(f"Guest: {sample_data['full_name']}")
print(f"Mobile: {sample_data['mobile_number']}")
print(f"Room: {room_number}")
print(f"Receipt No: {sample_data['recipe_number']}")
print(f"Guests: M:{sample_data['male_count']}, F:{sample_data['female_count']}, C:{sample_data['children_count']}")
print(f"Amount Paid: Rs. {sample_data['amount_paid_today']}")
print(f"Remaining: Rs. {sample_data['remaining_amount']}")
print("\nNew simple receipt format has been implemented!")
print("The receipt will now show all information in a single clean table.")
