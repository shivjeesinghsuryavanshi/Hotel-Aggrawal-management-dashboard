"""
Enhanced Receipt System Functions for Hotel Management
This module provides functions for:
1. Sequential receipt number generation
2. Custom PDF receipt with Hindi fonts
3. Search and filter system
"""

import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
import tempfile
import os

DATABASE_PATH = 'hotel_management.db'

def get_next_receipt_number():
    """Generate and return the next sequential receipt number"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Get current number and increment it
        cursor.execute('SELECT current_number FROM receipt_counter WHERE id = 1')
        current_number = cursor.fetchone()[0]
        
        next_number = current_number + 1
        
        # Update the counter
        cursor.execute('UPDATE receipt_counter SET current_number = ?, last_updated = ? WHERE id = 1', 
                      (next_number, datetime.now()))
        
        conn.commit()
        return str(next_number).zfill(6)  # Return as 6-digit string (e.g., "001001")
        
    except Exception as e:
        print(f"Error generating receipt number: {e}")
        return None
    finally:
        conn.close()

def generate_receipt_with_number(tourist_id, generated_by='admin'):
    """Generate receipt number for an existing tourist record (only if check-in is completed)"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if tourist exists and check-in is completed
        cursor.execute('SELECT recipe_number, check_in_done FROM tourists WHERE id = ?', (tourist_id,))
        result = cursor.fetchone()
        
        if not result:
            return None, "Tourist record not found"
        
        receipt_number, check_in_done = result
        already_generated = bool(receipt_number and receipt_number.strip())
        
        # Check if check-in is completed
        if not check_in_done:
            return None, "Receipt can only be generated after check-in is completed"
        
        if already_generated and receipt_number:
            return receipt_number, "Receipt already generated"
        
        # Generate new receipt number
        receipt_number = get_next_receipt_number()
        
        if not receipt_number:
            return None, "Failed to generate receipt number"
        
        # Update tourist record
        cursor.execute('''
            UPDATE tourists 
            SET recipe_number = ?
            WHERE id = ?
        ''', (receipt_number, tourist_id))
        
        conn.commit()
        return receipt_number, "Receipt generated successfully"
        
    except Exception as e:
        return None, f"Error: {str(e)}"
    finally:
        conn.close()

def generate_custom_hindi_receipt(tourist_data, receipt_number):
    """Generate professional hotel receipt matching the uploaded format"""
    
    # Ensure receipt_number is a string, not a tuple
    if isinstance(receipt_number, tuple):
        receipt_number = str(receipt_number[0]) if receipt_number[0] else "UNKNOWN"
    elif not receipt_number:
        receipt_number = "UNKNOWN"
    else:
        receipt_number = str(receipt_number)
    
    # Create temporary file for PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_filename = temp_file.name
    temp_file.close()
    
    # Create canvas for custom positioning
    c = canvas.Canvas(temp_filename, pagesize=A4)
    width, height = A4
    
    # Use standard fonts only (no Hindi fonts needed)
    # All text will be in English to avoid font rendering issues
    
    # Header background (Light Grey)
    c.setFillColor(colors.lightgrey)
    c.rect(0, height-100, width, 100, fill=1, stroke=1)
    
    # Hotel name and title (Black text on light grey background)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(width/2, height-40, "🏨 HOTEL RECEIPT 🏨")
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height-65, "Hotel Management System")
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, height-85, "★★★★ Premium Hotel Services ★★★★")
    
    # Receipt number box (Left side) - Professional design
    box_width = 200
    box_height = 60
    left_x = 50
    right_x = width - 250
    box_y = height - 170
    
    # Receipt number main box
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    c.rect(left_x, box_y, box_width, box_height, fill=1, stroke=1)
    
    # Receipt number header section
    c.setFillColor(colors.lightgrey)
    c.setStrokeColor(colors.black)
    c.rect(left_x, box_y + 35, box_width, 25, fill=1, stroke=1)
    
    # Receipt number header text
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(left_x + box_width/2, box_y + 44, "RECEIPT NUMBER")
    
    # Receipt number value
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(left_x + box_width/2, box_y + 15, f"#{receipt_number}")
    
    # Date box (Right side) - Professional design
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    c.rect(right_x, box_y, box_width, box_height, fill=1, stroke=1)
    
    # Date header section
    c.setFillColor(colors.lightgrey)
    c.setStrokeColor(colors.black)
    c.rect(right_x, box_y + 35, box_width, 25, fill=1, stroke=1)
    
    # Date header text
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(right_x + box_width/2, box_y + 44, "DATE & TIME")
    
    # Date value
    current_date = datetime.now().strftime('%d/%m/%Y')
    current_time = datetime.now().strftime('%I:%M %p')
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(right_x + box_width/2, box_y + 22, current_date)
    c.setFont("Helvetica", 12)
    c.drawCentredString(right_x + box_width/2, box_y + 8, current_time)
    
    # Guest details section header
    y_pos = height - 210
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y_pos, "GUEST DETAILS")
    
    # Guest details box with better border
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    c.rect(50, y_pos-160, width-100, 150, fill=1, stroke=1)
    
    y_pos -= 25
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    
    # Name
    guest_name = tourist_data.get('full_name', '')
    c.drawString(60, y_pos, f"Name: {guest_name}")
    y_pos -= 20
    
    # Father/Spouse name
    father_spouse = tourist_data.get('father_spouse_name', '')
    if father_spouse:
        c.drawString(60, y_pos, f"S/o, W/o: {father_spouse}")
        y_pos -= 20
    
    # Address
    address = tourist_data.get('address', '')
    c.drawString(60, y_pos, f"Address: {address}")
    y_pos -= 20
    
    # Contact details (Mobile and Aadhar on same line)
    mobile = tourist_data.get('mobile_number', '')
    aadhar = tourist_data.get('aadhar_number', '')
    c.drawString(60, y_pos, f"Mobile: {mobile}")
    c.drawString(350, y_pos, f"Aadhar: {aadhar}")
    y_pos -= 30
    
    # Stay details section header
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y_pos, "STAY DETAILS")
    
    # Stay details box with better border
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    c.rect(50, y_pos-120, width-100, 110, fill=1, stroke=1)
    
    y_pos -= 25
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    
    # Room number and extra bed
    room_num = tourist_data.get('room_number', '')
    extra_bed = 'Yes' if tourist_data.get('extra_bed') else 'No'
    c.drawString(60, y_pos, f"Room No: {room_num}")
    c.drawString(350, y_pos, f"Extra Bed: {extra_bed}")
    y_pos -= 20
    
    # Check-in and check-out dates
    checkin_date = tourist_data.get('check_in_date', datetime.now().strftime('%Y-%m-%d'))
    checkout_date = tourist_data.get('check_out_date', '___________')
    c.drawString(60, y_pos, f"Check-in: {checkin_date}")
    c.drawString(350, y_pos, f"Check-out: {checkout_date}")
    y_pos -= 60  # Increased spacing from 30 to 60
    
    # Payment details section header
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y_pos, "PAYMENT DETAILS")
    
    # Simple payment amount display - only total
    y_pos -= 60  # Increased spacing to shift total amount box down
    
    # Calculate total amount
    total_amount = float(tourist_data.get('amount_paid_today', 0)) + float(tourist_data.get('remaining_amount', 0))
    
    # Total amount box - improved design
    table_x = 80  # More centered positioning
    box_width = 400  # Slightly narrower for better proportions
    box_height = 80  # Increased height for better spacing
    
    # Total amount box - white background with better border
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.black)
    c.setLineWidth(2)  # Thicker border for emphasis
    c.rect(table_x, y_pos, box_width, box_height, fill=1, stroke=1)
    
    # Header section within the box
    c.setFillColor(colors.lightgrey)
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.rect(table_x, y_pos + 50, box_width, 30, fill=1, stroke=1)
    
    # Total amount header text
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(table_x + box_width/2, y_pos + 60, "TOTAL AMOUNT")
    
    # Total amount value with better formatting
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 24)
    total_text = f"₹ {total_amount:,.2f}"  # Added comma separator
    c.drawCentredString(table_x + box_width/2, y_pos + 25, total_text)
    
    # Payment mode - positioned below total with better spacing
    payment_mode = tourist_data.get('payment_mode', 'Cash')
    payment_mode_english = {
        'Cash': 'Cash',
        'Cheque': 'Cheque', 
        'Online': 'Online',
        'Card': 'Card'
    }.get(payment_mode, 'Cash')
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(table_x + 10, y_pos - 30, f"Payment Mode: {payment_mode_english}")
    
    # Update y_pos for next section with better spacing
    y_pos -= 100  # Increased spacing to prevent overlap with Terms & Conditions
    
    # Footer section with terms and conditions
    c.setFillColor(colors.lightgrey)
    c.rect(50, y_pos, width-100, 80, fill=1, stroke=1)
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width/2, y_pos + 60, "Terms & Conditions")
    
    c.setFont("Helvetica", 10)
    terms_text = [
        "• Check-out time: 11:00 AM",
        "• Late check-out charges may apply",
        "• Room charges are non-refundable",
        "• Damages to hotel property will be charged"
    ]
    
    for i, term in enumerate(terms_text):
        c.drawString(60, y_pos + 40 - (i * 12), term)
    
    # Bottom signature section
    y_pos -= 120
    c.setFillColor(colors.lightgrey)
    c.rect(0, 0, width, 150, fill=1, stroke=1)
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, y_pos + 80, "Thank You for Staying with Us!")
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, y_pos + 60, "We hope you had a pleasant stay!")
    
    # Signature areas
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawString(70, y_pos + 30, "Guest Signature")
    c.drawString(70, y_pos + 15, "")
    c.drawString(70, y_pos - 5, "_" * 25)
    
    c.drawString(width-200, y_pos + 30, "Authorized Signature")
    c.drawString(width-200, y_pos + 15, "")  
    c.drawString(width-200, y_pos - 5, "_" * 25)
    
    # Generation info
    c.setFont("Helvetica", 8)
    c.drawCentredString(width/2, 25, f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    c.drawCentredString(width/2, 15, f"Receipt ID: {receipt_number}")
    
    # Save PDF
    c.save()
    
    return temp_filename

def search_tourists(search_term="", receipt_filter="", date_from="", date_to="", payment_mode=""):
    """Advanced search and filter function for tourists"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Base query (using actual database schema)
    query = '''
        SELECT id, full_name, mobile_number, aadhar_number, room_number, 
               check_in_date, amount_paid_today, remaining_amount, recipe_number, 
               check_in_done, payment_mode
        FROM tourists 
        WHERE 1=1
    '''
    
    params = []
    
    # Search term filter (name, mobile, aadhar, receipt number)
    if search_term:
        query += '''
            AND (full_name LIKE ? OR mobile_number LIKE ? OR 
                 aadhar_number LIKE ? OR recipe_number LIKE ?)
        '''
        search_pattern = f"%{search_term}%"
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern])
    
    # Receipt filter
    if receipt_filter == "yes":
        query += " AND recipe_number IS NOT NULL AND recipe_number != ''"
    elif receipt_filter == "no":
        query += " AND (recipe_number IS NULL OR recipe_number = '')"
    
    # Date range filter
    if date_from:
        query += " AND check_in_date >= ?"
        params.append(date_from)
    
    if date_to:
        query += " AND check_in_date <= ?"
        params.append(date_to)
    
    # Payment mode filter
    if payment_mode:
        query += " AND payment_mode = ?"
        params.append(payment_mode)
    
    # Order by most recent
    query += " ORDER BY created_at DESC"
    
    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        tourists = []
        for row in results:
            tourist = {
                'id': row[0],
                'full_name': row[1],
                'father_spouse_name': '',  # Default empty for current schema
                'mobile_number': row[2],
                'aadhar_number': row[3],
                'room_number': row[4],
                'check_in_date': row[5],
                'amount_paid_today': row[6],
                'remaining_amount': row[7],
                'recipe_number': row[8],
                'receipt_number': row[8],  # Map recipe_number to receipt_number for compatibility
                'check_in_done': row[9],
                'payment_mode': row[10],
                'receipt_generated': bool(row[8] and row[8].strip())  # True if recipe_number exists
            }
            tourists.append(tourist)
        
        return tourists, None
        
    except Exception as e:
        return [], f"Search error: {str(e)}"
    finally:
        conn.close()

def get_tourist_full_data(tourist_id):
    """Get complete tourist data for receipt generation"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, full_name, father_spouse_name, age, work, address, 
                   aadhar_number, mobile_number, alternate_mobile, gender, 
                   children_count, amount_paid_today, remaining_amount, check_in_done, 
                   room_number, check_in_date, check_out_date, check_out_time, 
                   extra_bed, recipe_number, comments, created_at
            FROM tourists 
            WHERE id = ?
        ''', (tourist_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        tourist_data = {
            'id': row[0],
            'full_name': row[1],
            'father_spouse_name': row[2] if row[2] else '',
            'age': row[3] if row[3] else '',
            'work': row[4] if row[4] else '',
            'address': row[5],
            'aadhar_number': row[6],
            'mobile_number': row[7],
            'alternate_mobile': row[8] if row[8] else '',
            'gender': row[9] if row[9] else '',
            'children_count': row[10] if row[10] else 0,
            'amount_paid_today': row[11],
            'remaining_amount': row[12],
            'check_in_done': row[13],
            'room_number': row[14],
            'check_in_date': row[15],
            'check_out_date': row[16] if row[16] else '',
            'check_out_time': row[17] if row[17] else '',
            'extra_bed': row[18] if row[18] else False,
            'recipe_number': row[19],
            'receipt_number': row[19],  # Map recipe_number to receipt_number for compatibility
            'comments': row[20] if row[20] else '',
            'created_at': row[21],
            'payment_mode': 'Cash',  # Default for current schema
            'receipt_generated': bool(row[19] and row[19].strip()),  # True if recipe_number exists
            'receipt_generated_date': '',  # Not in current schema
            'receipt_generated_by': '',  # Not in current schema
            # Additional fields that might be needed by templates
            'male_count': 0,  # Not in current schema
            'female_count': 0  # Not in current schema
        }
        
        return tourist_data
        
    except Exception as e:
        print(f"Error fetching tourist data: {e}")
        return None
    finally:
        conn.close()
