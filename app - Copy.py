"""
Aggarwal Bhawan, Haridwar - Main Flask Application
This is the main entry point for the Aggarwal Bhawan management web application.
Handles 157 rooms with tourist check-in, PDF receipts, Excel reports, calendar view, and search functionality.
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_session import Session
import sqlite3
import hashlib
import os
import pandas as pd
from datetime import datetime, timedelta
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import tempfile
import re
from receipt_system import (
    get_next_receipt_number, 
    generate_receipt_with_number, 
    generate_custom_hindi_receipt,
    search_tourists,
    get_tourist_full_data
)

app = Flask(__name__)
app.secret_key = 'aggarwal_bhawan_secret_key_2025'  # Change this in production

# Configure session to use filesystem
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Constants
TOTAL_ROOMS = 157
DATABASE_PATH = 'hotel_management.db'

def init_database():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create users table for login system
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create tourists table for check-in data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tourists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            father_spouse_name TEXT,
            age INTEGER,
            work TEXT,
            address TEXT NOT NULL,
            area TEXT NOT NULL,
            pincode INTEGER NOT NULL,
            aadhar_number TEXT NOT NULL,
            mobile_number TEXT NOT NULL,
            alternate_mobile TEXT,
            email TEXT NOT NULL,
            gender TEXT,
            children_count INTEGER DEFAULT 0,
            amount_paid_today REAL NOT NULL,
            remaining_amount REAL NOT NULL,
            check_in_done BOOLEAN NOT NULL,
            room_number INTEGER NOT NULL,
            check_in_date DATE NOT NULL,
            check_out_date DATE,
            check_out_time TIME,
            extra_bed BOOLEAN DEFAULT FALSE,
            recipe_number TEXT,
            comments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create default admin user if not exists
    cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone()[0] == 0:
        # Default password: admin123 (change this in production)
        password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                      ('admin', password_hash))
    
    conn.commit()
    conn.close()

def validate_form_data(data):
    """Validate tourist form data"""
    errors = []
    
    # Validate Aadhar (12 digits)
    if not re.match(r'^\d{12}$', data.get('aadhar_number', '')):
        errors.append('Aadhar number must be exactly 12 digits')
    
    # Validate Mobile (10 digits)
    if not re.match(r'^\d{10}$', data.get('mobile_number', '')):
        errors.append('Mobile number must be exactly 10 digits')
    
    # Validate Alternate Mobile (10 digits, optional)
    alternate_mobile = data.get('alternate_mobile', '').strip()
    if alternate_mobile and not re.match(r'^\d{10}$', alternate_mobile):
        errors.append('Alternate mobile number must be exactly 10 digits')
      # Email and Pincode validation removed as these fields no longer exist
    
    # Validate Age (optional, but if provided should be reasonable)
    age = data.get('age', '').strip()
    if age:
        try:
            age_int = int(age)
            if age_int < 1 or age_int > 120:
                errors.append('Age must be between 1 and 120')
        except ValueError:
            errors.append('Age must be a valid number')
    
    # Validate Children Count (optional, but if provided should be reasonable)
    children = data.get('children_count', '').strip()
    if children:
        try:
            children_int = int(children)
            if children_int < 0 or children_int > 20:
                errors.append('Children count must be between 0 and 20')
        except ValueError:
            errors.append('Children count must be a valid number')
    
    # Validate Male Count (optional, but if provided should be reasonable)
    male_count = data.get('male_count', '').strip()
    if male_count:
        try:
            male_count_int = int(male_count)
            if male_count_int < 0 or male_count_int > 50:
                errors.append('Male count must be between 0 and 50')
        except ValueError:
            errors.append('Male count must be a valid number')
    
    # Validate Female Count (optional, but if provided should be reasonable)
    female_count = data.get('female_count', '').strip()
    if female_count:
        try:
            female_count_int = int(female_count)
            if female_count_int < 0 or female_count_int > 50:
                errors.append('Female count must be between 0 and 50')
        except ValueError:
            errors.append('Female count must be a valid number')
    
    # Validate amounts
    try:
        amount_paid = float(data.get('amount_paid_today', 0))
        if amount_paid < 0:
            errors.append('Amount paid cannot be negative')
    except ValueError:
        errors.append('Amount paid must be a valid number')
    
    try:
        remaining = float(data.get('remaining_amount', 0))
        if remaining < 0:
            errors.append('Remaining amount cannot be negative')
    except ValueError:
        errors.append('Remaining amount must be a valid number')
    
    return errors

def get_next_available_room():
    """Get the next available room number (1-157)"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get occupied rooms for today
    today = datetime.now().date()
    cursor.execute('SELECT room_number FROM tourists WHERE check_in_date = ? AND check_in_done = 1', 
                   (today,))
    occupied_rooms = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    # Find first available room
    for room_num in range(1, TOTAL_ROOMS + 1):
        if room_num not in occupied_rooms:
            return room_num
    
    return None  # No rooms available

def generate_pdf_receipt(tourist_data, room_number):
    """Generate simple PDF receipt for tourist check-in"""
    # Create temporary file for PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_filename = temp_file.name
    temp_file.close()
    
    # Create PDF document
    doc = SimpleDocTemplate(temp_filename, pagesize=letter, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    story = []
    
    # Hotel Header
    header_style = ParagraphStyle(
        'HotelHeader',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=5,
        alignment=1,  # Center alignment
        textColor=colors.black
    )
    story.append(Paragraph("AGGARWAL BHAWAN", header_style))
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=15,
        alignment=1,
        textColor=colors.black
    )
    story.append(Paragraph("Haridwar", subtitle_style))
    
    # Receipt Title
    title_style = ParagraphStyle(
        'ReceiptTitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=15,
        alignment=1,
        textColor=colors.black
    )
    story.append(Paragraph("CHECK-IN RECEIPT", title_style))
    
    # Receipt Number and Date
    receipt_num = tourist_data.get('recipe_number', 'N/A')
    current_date = datetime.now().strftime('%d-%m-%Y')
    current_time = datetime.now().strftime('%H:%M')
    
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=20,
        alignment=1
    )
    story.append(Paragraph(f"Receipt No: {receipt_num} | Date: {current_date} | Time: {current_time}", info_style))
    
    # Calculate amounts
    try:
        amount_paid = float(tourist_data['amount_paid_today']) if tourist_data['amount_paid_today'] else 0.0
        remaining_amount = float(tourist_data['remaining_amount']) if tourist_data['remaining_amount'] else 0.0
        total_amount = amount_paid + remaining_amount
    except (ValueError, TypeError):
        amount_paid = 0.0
        remaining_amount = 0.0
        total_amount = 0.0
    
    # Group composition
    male_count = int(tourist_data.get('male_count', 0))
    female_count = int(tourist_data.get('female_count', 0))
    children_count = int(tourist_data.get('children_count', 0))
    total_guests = male_count + female_count + children_count
    
    # All details in one simple table
    data = [
        ['Guest Name:', tourist_data['full_name']],
        ['Father/Spouse:', tourist_data.get('father_spouse_name', 'N/A')],
        ['Mobile Number:', tourist_data['mobile_number']],
        ['Address:', tourist_data.get('address', 'N/A')],
        ['ID Number:', tourist_data.get('aadhar_number', 'N/A')],
        ['', ''],  # Empty row for spacing
        ['Room Number:', f"Room {room_number}"],
        ['Check-in Date:', current_date],
        ['Check-out Date:', tourist_data.get('check_out_date', 'Not specified')],
        ['Total Guests:', f"{total_guests} (M:{male_count}, F:{female_count}, C:{children_count})"],
        ['Extra Bed:', 'Yes' if tourist_data.get('extra_bed') else 'No'],
        ['', ''],  # Empty row for spacing
        ['Amount Paid:', f"Rs. {amount_paid:.2f}"],
        ['Remaining Amount:', f"Rs. {remaining_amount:.2f}"],
        ['Total Amount:', f"Rs. {total_amount:.2f}"],
        ['Payment Mode:', tourist_data.get('payment_mode', 'Cash')]
    ]
    
    table = Table(data, colWidths=[2.2*inch, 3.8*inch])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Bold first column
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        # Highlight amount rows
        ('BACKGROUND', (0, 12), (-1, 14), colors.lightgrey),
        ('FONTNAME', (0, 14), (-1, 14), 'Helvetica-Bold'),  # Bold total amount
    ]))
    
    story.append(table)
    story.append(Spacer(1, 30))
    
    # Simple footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        alignment=1,
        textColor=colors.black
    )
    
    story.append(Paragraph("Thank you for choosing Aggarwal Bhawan!", footer_style))
    story.append(Paragraph("Check-in: 12:00 PM | Check-out: 11:00 AM", footer_style))
    
    # Build PDF
    doc.build(story)
    
    return temp_filename

@app.route('/')
def index():
    """Main dashboard route"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get dashboard statistics
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().date()
    
    # Get today's check-ins
    cursor.execute('SELECT COUNT(*) FROM tourists WHERE check_in_date = ? AND check_in_done = 1', (today,))
    checked_in_today = cursor.fetchone()[0]
    
    # Calculate available rooms
    available_today = TOTAL_ROOMS - checked_in_today
    
    # Get recent check-ins for table display
    cursor.execute('''
        SELECT full_name, mobile_number, aadhar_number, amount_paid_today, 
               remaining_amount, check_in_done, room_number, check_in_date,
               CASE WHEN recipe_number IS NOT NULL AND recipe_number != '' THEN 1 ELSE 0 END as receipt_generated, 
               id, recipe_number
        FROM tourists 
        ORDER BY created_at DESC 
        LIMIT 10
    ''')
    recent_checkins = cursor.fetchall()
    
    conn.close()
    
    dashboard_stats = {
        'total_rooms': TOTAL_ROOMS,
        'checked_in_today': checked_in_today,
        'available_today': available_today,
        'recent_checkins': recent_checkins
    }
    
    return render_template('dashboard.html', stats=dashboard_stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if request.method == 'POST':
        print("=== LOGIN ATTEMPT ===")  # Debug
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        print(f"Username: '{username}'")  # Debug
        print(f"Password length: {len(password)}")  # Debug
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('login.html')
        
        # Hash password for comparison
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        print(f"Password hash: {password_hash}")  # Debug
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, username FROM users WHERE username = ? AND password_hash = ?', 
                      (username, password_hash))
        user = cursor.fetchone()
        
        # Debug: Check if user exists
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', (username,))
        user_exists = cursor.fetchone()[0]
        print(f"User exists: {user_exists}")  # Debug
        
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash('Login successful!', 'success')
            print("Login successful, redirecting to dashboard")  # Debug
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
            print("Login failed")  # Debug
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout route"""
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    """Tourist check-in form route"""
    print(f"=== CHECKIN ROUTE ===")
    print(f"Method: {request.method}")
    print(f"Session user_id: {session.get('user_id')}")
    
    if 'user_id' not in session:
        print("No user session, redirecting to login")
        return redirect(url_for('login'))
    
    # Get available rooms for the form
    today = datetime.now().date()
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get occupied rooms for today
    cursor.execute('SELECT room_number FROM tourists WHERE check_in_date = ? AND check_in_done = 1', 
                   (today,))
    occupied_rooms = [row[0] for row in cursor.fetchall()]
    
    # Get available rooms
    available_rooms = []
    for room_num in range(1, TOTAL_ROOMS + 1):
        if room_num not in occupied_rooms:
            available_rooms.append(room_num)
    
    conn.close()
    print(f"Available rooms: {len(available_rooms)} out of {TOTAL_ROOMS}")
    
    if request.method == 'POST':
        print("=== FORM SUBMISSION RECEIVED ===")
        print(f"Request headers: {dict(request.headers)}")
        print(f"Form data keys: {list(request.form.keys())}")
        print(f"Form data values: {dict(request.form)}")
        
        # Get form data with proper type handling
        form_data = {
            'full_name': request.form.get('full_name', '').strip(),
            'address': request.form.get('address', '').strip(),
            'aadhar_number': request.form.get('aadhar_number', '').strip(),
            'mobile_number': request.form.get('mobile_number', '').strip(),
            'amount_paid_today': request.form.get('amount_paid_today', '0').strip(),
            'remaining_amount': request.form.get('remaining_amount', '0').strip(),
            'check_in_done': request.form.get('check_in_done') == 'yes',
            'room_number': request.form.get('room_number', '').strip(),
            'payment_mode': request.form.get('payment_mode', 'Cash').strip(),
            'male_count': request.form.get('male_count', '0').strip(),
            'female_count': request.form.get('female_count', '0').strip()
        }
        
        print(f"Processed form data: {form_data}")
        
        # Validate form data
        validation_errors = validate_form_data(form_data)
        
        # Validate room selection
        if not form_data['room_number']:
            validation_errors.append('Please select a room number')
        else:
            try:
                selected_room = int(form_data['room_number'])
                if selected_room not in available_rooms:
                    validation_errors.append('Selected room is not available')
                    print(f"❌ Room {selected_room} not available. Available rooms: {available_rooms[:10]}...")
            except ValueError:
                validation_errors.append('Invalid room number selected')
                print(f"❌ Invalid room number: {form_data['room_number']}")
        
        print(f"Validation errors: {validation_errors}")
        
        if validation_errors:
            print("❌ Validation failed, returning form with errors")
            for error in validation_errors:
                flash(error, 'error')
            return render_template('checkin.html', form_data=form_data, available_rooms=available_rooms)
        
        # Use selected room number
        room_number = int(form_data['room_number'])
        print(f"Assigning room: {room_number}")
        
        # Save to database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        try:
            print(f"📝 Executing database insert...")
            print(f"   SQL: INSERT INTO tourists (full_name, address, aadhar_number, mobile_number, amount_paid_today, remaining_amount, check_in_done, room_number, check_in_date)")
            
            # Convert data types safely
            try:
                amount_paid_float = float(form_data['amount_paid_today']) if form_data['amount_paid_today'] else 0.0
                remaining_amount_float = float(form_data['remaining_amount']) if form_data['remaining_amount'] else 0.0
                age_int = int(form_data['age']) if form_data.get('age') and form_data['age'].strip() else None
                children_int = int(form_data['children_count']) if form_data.get('children_count') and form_data['children_count'].strip() else 0
                male_count_int = int(form_data['male_count']) if form_data.get('male_count') and form_data['male_count'].strip() else 0
                female_count_int = int(form_data['female_count']) if form_data.get('female_count') and form_data['female_count'].strip() else 0
                extra_bed_bool = form_data.get('extra_bed') == 'on'
            except ValueError as ve:
                print(f"❌ Type conversion error: {str(ve)}")
                print(f"   amount_paid_today: '{form_data['amount_paid_today']}'")
                print(f"   remaining_amount: '{form_data['remaining_amount']}'")
                print(f"   age: '{form_data.get('age', '')}'")
                print(f"   children_count: '{form_data.get('children_count', '')}'")
                print(f"   male_count: '{form_data.get('male_count', '')}'")
                print(f"   female_count: '{form_data.get('female_count', '')}'")
                raise ValueError(f"Invalid number format in form data: {str(ve)}")
            
            print(f"   Values: {(form_data['full_name'], form_data['address'], form_data['aadhar_number'], form_data['mobile_number'], amount_paid_float, remaining_amount_float, form_data['check_in_done'], room_number, datetime.now().date())}")
            
            # Generate automatic receipt number
            receipt_number = generate_receipt_number()
            print(f"📄 Generated receipt number: {receipt_number}")
            
            cursor.execute('''
                INSERT INTO tourists 
                (full_name, father_spouse_name, age, work, address, aadhar_number, 
                 mobile_number, alternate_mobile, gender, male_count, female_count, children_count, amount_paid_today, 
                 remaining_amount, check_in_done, room_number, check_in_date, check_out_date, 
                 check_out_time, extra_bed, recipe_number, comments, payment_mode)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                form_data['full_name'], form_data.get('father_spouse_name', ''), age_int, 
                form_data.get('work', ''), form_data['address'], form_data['aadhar_number'], 
                form_data['mobile_number'], form_data.get('alternate_mobile', ''), 
                form_data.get('gender', ''), male_count_int, female_count_int, children_int, amount_paid_float, 
                remaining_amount_float, form_data['check_in_done'], room_number, datetime.now().date(),
                form_data.get('check_out_date', ''), form_data.get('check_out_time', ''), extra_bed_bool,
                receipt_number, form_data.get('comments', ''), form_data.get('payment_mode', 'Cash')
            ))
            
            print(f"📝 Database insert executed, committing...")
            conn.commit()
            print("✅ Database insert successful")
            
            # Verify the insert worked
            cursor.execute("SELECT COUNT(*) FROM tourists WHERE room_number = ? AND check_in_date = ?", 
                          (room_number, datetime.now().date()))
            count = cursor.fetchone()[0]
            print(f"✅ Verification: {count} record(s) found for room {room_number} today")
            
            # Add receipt number to form_data for PDF generation
            form_data['recipe_number'] = receipt_number
            
            # Generate PDF receipt
            pdf_path = generate_pdf_receipt(form_data, room_number)
            print(f"✅ PDF generated: {pdf_path}")
            
            success_message = f'✅ Check-in successful! Room {room_number} assigned to {form_data["full_name"]}. Receipt No: {receipt_number}. PDF receipt generated.'
            flash(success_message, 'success')
            print(f"✅ Success message: {success_message}")
            
            # Store PDF path in session for download
            session['latest_receipt'] = pdf_path
            print(f"✅ PDF stored in session for download")
            
            conn.close()
            print("✅ Redirecting to dashboard...")
            return redirect(url_for('index'))
            
        except sqlite3.IntegrityError as e:
            print(f"❌ Database integrity error: {str(e)}")
            conn.rollback()
            conn.close()
            flash(f'Database integrity error: {str(e)}. Please check if the room is already occupied.', 'error')
            return render_template('checkin.html', form_data=form_data, available_rooms=available_rooms)
        except sqlite3.OperationalError as e:
            print(f"❌ Database operational error: {str(e)}")
            conn.rollback()
            conn.close()
            flash(f'Database operational error: {str(e)}. Please try again.', 'error')
            return render_template('checkin.html', form_data=form_data, available_rooms=available_rooms)
        except ValueError as e:
            print(f"❌ Data conversion error: {str(e)}")
            conn.rollback()
            conn.close()
            flash(f'Data format error: {str(e)}. Please check your input values.', 'error')
            return render_template('checkin.html', form_data=form_data, available_rooms=available_rooms)
        except Exception as e:
            print(f"❌ Unexpected database error: {str(e)}")
            print(f"❌ Error type: {type(e).__name__}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            conn.rollback()
            conn.close()
            flash(f'Unexpected error during check-in: {str(e)}', 'error')
            return render_template('checkin.html', form_data=form_data, available_rooms=available_rooms)
    
    print("Rendering checkin form")
    return render_template('checkin.html', available_rooms=available_rooms)

@app.route('/download_receipt')
def download_receipt():
    """Download the latest generated PDF receipt"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    pdf_path = session.get('latest_receipt')
    if pdf_path and os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True, download_name='hotel_receipt.pdf')
    else:
        flash('No receipt available for download', 'error')
        return redirect(url_for('index'))

@app.route('/export_excel')
def export_excel():
    """Export monthly report to Excel"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get current month's data
    current_month = datetime.now().replace(day=1)
    next_month = (current_month + timedelta(days=32)).replace(day=1)
    
    conn = sqlite3.connect(DATABASE_PATH)
    
    # Query for current month
    query = '''
        SELECT check_in_date, full_name, mobile_number, aadhar_number, 
               amount_paid_today, remaining_amount, check_in_done, room_number
        FROM tourists 
        WHERE check_in_date >= ? AND check_in_date < ?
        ORDER BY check_in_date, created_at
    '''
    
    df = pd.read_sql_query(query, conn, params=(current_month.date(), next_month.date()))
    conn.close()
    
    if df.empty:
        flash('No data available for current month', 'info')
        return redirect(url_for('index'))
    
    # Create Excel file with formatting
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    temp_filename = temp_file.name
    temp_file.close()
    
    with pd.ExcelWriter(temp_filename, engine='openpyxl') as writer:
        # Group by date and create formatted sheet
        current_row = 0
        
        for date, group in df.groupby('check_in_date'):
            # Write date header
            date_df = pd.DataFrame([['Date: ' + str(date)]], columns=[''])
            date_df.to_excel(writer, sheet_name='Monthly Report', 
                           startrow=current_row, index=False, header=False)
            current_row += 2
            
            # Write group data
            group_display = group[['full_name', 'mobile_number', 'aadhar_number', 
                                 'amount_paid_today', 'remaining_amount', 'check_in_done', 'room_number']]
            group_display.columns = ['Name', 'Mobile', 'Aadhar', 'Amount Paid Today', 
                                   'Remaining Amount', 'Check-In', 'Room Number']
            
            group_display.to_excel(writer, sheet_name='Monthly Report', 
                                 startrow=current_row, index=False)
            current_row += len(group_display) + 1
            
            # Add subtotal row
            daily_paid = group['amount_paid_today'].sum()
            daily_remaining = group['remaining_amount'].sum()
            subtotal_df = pd.DataFrame([['', '', '', f'Daily Total: ₹{daily_paid:.2f}', 
                                       f'₹{daily_remaining:.2f}', '', '']], 
                                     columns=group_display.columns)
            subtotal_df.to_excel(writer, sheet_name='Monthly Report', 
                                startrow=current_row, index=False, header=False)
            current_row += 3
        
        # Add grand total
        total_paid = df['amount_paid_today'].sum()
        total_remaining = df['remaining_amount'].sum()
        grand_total_df = pd.DataFrame([['', '', 'GRAND TOTAL:', f'₹{total_paid:.2f}', 
                                      f'₹{total_remaining:.2f}', '', '']], 
                                     columns=['', '', '', '', '', '', ''])
        grand_total_df.to_excel(writer, sheet_name='Monthly Report', 
                               startrow=current_row, index=False, header=False)
    
    return send_file(temp_filename, as_attachment=True, 
                    download_name=f'hotel_report_{current_month.strftime("%Y_%m")}.xlsx')

@app.route('/api/room_status')
def api_room_status():
    """API endpoint for room status data"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    today = datetime.now().date()
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT room_number FROM tourists WHERE check_in_date = ? AND check_in_done = 1', 
                   (today,))
    occupied_rooms = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    room_status = {}
    for room_num in range(1, TOTAL_ROOMS + 1):
        room_status[room_num] = 'occupied' if room_num in occupied_rooms else 'available'
    
    return jsonify(room_status)

@app.route('/api/available_rooms')
def api_available_rooms():
    """API endpoint to get available rooms for today"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    today = datetime.now().date()
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get occupied rooms for today
    cursor.execute('SELECT room_number FROM tourists WHERE check_in_date = ? AND check_in_done = 1', 
                   (today,))
    occupied_rooms = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    # Get available rooms
    available_rooms = []
    for room_num in range(1, TOTAL_ROOMS + 1):
        if room_num not in occupied_rooms:
            available_rooms.append(room_num)
    
    return jsonify({
        'available_rooms': available_rooms,
        'total_rooms': TOTAL_ROOMS,
        'occupied_count': len(occupied_rooms),
        'available_count': len(available_rooms)
    })

@app.route('/test_db')
def test_db():
    """Test route to check database setup"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Check if users table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    table_exists = cursor.fetchone()
    
    # Check users in database
    cursor.execute("SELECT username, password_hash FROM users")
    users = cursor.fetchall()
    
    conn.close()
    
    result = {
        'table_exists': table_exists is not None,
        'users_count': len(users),
        'users': users
    }
    
    return jsonify(result)

@app.route('/test_login', methods=['POST'])
def test_login():
    """Test route to check form submission"""
    print("=== TEST LOGIN ROUTE ===")
    print(f"Form data: {request.form}")
    print(f"Username: {request.form.get('username')}")
    print(f"Password: {request.form.get('password')}")
    return jsonify({
        'form_data': dict(request.form),
        'method': request.method
    })

@app.route('/simple_login')
def simple_login():
    """Simple login page for testing"""
    return render_template('simple_login.html')

@app.route('/test_checkin')
def test_checkin():
    """Simple test check-in form"""
    return render_template('test_checkin.html')

@app.route('/simple_checkin')
def simple_checkin():
    """Simple check-in form without complex JavaScript"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get available rooms
    today = datetime.now().date()
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT room_number FROM tourists WHERE check_in_date = ? AND check_in_done = 1', 
                   (today,))
    occupied_rooms = [row[0] for row in cursor.fetchall()]
    
    available_rooms = []
    for room_num in range(1, TOTAL_ROOMS + 1):
        if room_num not in occupied_rooms:
            available_rooms.append(room_num)
    
    conn.close()
    
    return render_template('simple_checkin.html', available_rooms=available_rooms)

# Tourist Profile Management Routes
@app.route('/tourist_profiles')
def tourist_profiles():
    """Display all tourist profiles"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get all tourists with their information (using actual database schema)
    cursor.execute('''
        SELECT id, full_name, father_spouse_name, age, work, address, 
               aadhar_number, mobile_number, alternate_mobile, gender, 
               male_count, female_count, children_count, amount_paid_today, 
               remaining_amount, check_in_done, room_number, check_in_date, 
               check_out_date, check_out_time, extra_bed, recipe_number, 
               comments, created_at, payment_mode
        FROM tourists 
        ORDER BY created_at DESC
    ''')
    
    tourists = []
    for row in cursor.fetchall():
        tourist = {
            'id': row[0],
            'full_name': row[1],
            'father_spouse_name': row[2] or '',  # Handle None values
            'age': row[3],
            'work': row[4] or '',  # Handle None values
            'address': row[5],
            'aadhar_number': row[6],
            'mobile_number': row[7],
            'alternate_mobile': row[8] or '',  # Handle None values
            'gender': row[9] or '',  # Handle None values
            'male_count': row[10] or 0,  # Handle None values
            'female_count': row[11] or 0,  # Handle None values
            'children_count': row[12] or 0,  # Handle None values
            'amount_paid_today': row[13],
            'remaining_amount': row[14],
            'check_in_done': row[15],
            'room_number': row[16],
            'check_in_date': row[17],
            'check_out_date': row[18] or '',  # Handle None values
            'check_out_time': row[19] or '',  # Handle None values
            'extra_bed': row[20] or False,  # Handle None values
            'recipe_number': row[21] or '',  # Handle None values
            'comments': row[22] or '',  # Handle None values
            'created_at': row[23],
            'payment_mode': row[24] or 'Cash',  # Handle None values
            'receipt_generated': bool(row[21]),  # True if recipe_number exists
            'receipt_number': row[21] or ''  # Use recipe_number
        }
        tourists.append(tourist)
    
    conn.close()
    
    return render_template('tourist_profiles.html', tourists=tourists)

@app.route('/tourist_profile/<int:tourist_id>')
def tourist_profile_detail(tourist_id):
    """Display detailed view of a specific tourist"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, full_name, father_spouse_name, age, work, address, 
               aadhar_number, mobile_number, alternate_mobile, gender, 
               children_count, amount_paid_today, remaining_amount, check_in_done, 
               room_number, check_in_date, check_out_date, check_out_time, 
               extra_bed, recipe_number, comments, created_at, payment_mode
        FROM tourists 
        WHERE id = ?
    ''', (tourist_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        flash('Tourist profile not found', 'error')
        return redirect(url_for('tourist_profiles'))
    
    tourist = {
        'id': row[0],
        'full_name': row[1],
        'father_spouse_name': row[2] or '',  # Handle None values
        'age': row[3],
        'work': row[4] or '',  # Handle None values
        'address': row[5],
        'aadhar_number': row[6],
        'mobile_number': row[7],
        'alternate_mobile': row[8] or '',  # Handle None values
        'gender': row[9] or '',  # Handle None values
        'children_count': row[10] or 0,  # Handle None values
        'amount_paid_today': row[11],
        'remaining_amount': row[12],
        'check_in_done': row[13],
        'room_number': row[14],
        'check_in_date': row[15],
        'check_out_date': row[16] or '',  # Handle None values
        'check_out_time': row[17] or '',  # Handle None values
        'extra_bed': row[18] or False,  # Handle None values
        'recipe_number': row[19] or '',  # Handle None values
        'comments': row[20] or '',  # Handle None values
        'created_at': row[21],
        'payment_mode': row[22] or 'Cash',  # Handle None values
        'receipt_generated': False,  # Not in current schema
        'receipt_generated_date': '',  # Not in current schema
        'receipt_generated_by': '',  # Not in current schema
        'receipt_number': row[19] or ''  # Use recipe_number
    }
    
    return render_template('tourist_profile_detail.html', tourist=tourist)

@app.route('/tourist_profile/<int:tourist_id>/edit', methods=['GET', 'POST'])
def edit_tourist_profile(tourist_id):
    """Edit a tourist profile"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Get form data (only fields that exist in current schema)
        form_data = {
            'full_name': request.form.get('full_name', '').strip(),
            'address': request.form.get('address', '').strip(),
            'aadhar_number': request.form.get('aadhar_number', '').strip(),
            'mobile_number': request.form.get('mobile_number', '').strip(),
            'amount_paid_today': request.form.get('amount_paid_today', '').strip(),
            'remaining_amount': request.form.get('remaining_amount', '').strip(),
            'payment_mode': request.form.get('payment_mode', 'Cash')
        }
        
        # Validate form data
        errors = validate_form_data(form_data)
        
        if not errors:
            try:
                # Convert data types safely
                amount_paid_float = float(form_data['amount_paid_today']) if form_data['amount_paid_today'] else 0.0
                remaining_amount_float = float(form_data['remaining_amount']) if form_data['remaining_amount'] else 0.0
                
                # Update tourist profile (only fields that exist in current schema)
                cursor.execute('''
                    UPDATE tourists 
                    SET full_name = ?, address = ?, aadhar_number = ?, 
                        mobile_number = ?, amount_paid_today = ?, remaining_amount = ?, 
                        payment_mode = ?
                    WHERE id = ?
                ''', (
                    form_data['full_name'], form_data['address'], form_data['aadhar_number'], 
                    form_data['mobile_number'], amount_paid_float, remaining_amount_float, 
                    form_data['payment_mode'], tourist_id
                ))
                
                conn.commit()
                flash('Tourist profile updated successfully!', 'success')
                return redirect(url_for('tourist_profile_detail', tourist_id=tourist_id))
                
            except ValueError as e:
                flash(f'Invalid data format: {str(e)}', 'error')
            except Exception as e:
                flash(f'Error updating profile: {str(e)}', 'error')
        else:
            for error in errors:
                flash(error, 'error')
    
    # Get current tourist data
    cursor.execute('''
        SELECT id, full_name, father_spouse_name, age, work, address, 
               aadhar_number, mobile_number, alternate_mobile, gender, 
               children_count, amount_paid_today, remaining_amount, check_in_done, 
               room_number, check_in_date, check_out_date, check_out_time, 
               extra_bed, recipe_number, comments, created_at, payment_mode
        FROM tourists 
        WHERE id = ?
    ''', (tourist_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        flash('Tourist profile not found', 'error')
        return redirect(url_for('tourist_profiles'))
    
    tourist = {
        'id': row[0],
        'full_name': row[1],
        'father_spouse_name': row[2] or '',  # Handle None values
        'age': row[3],
        'work': row[4] or '',  # Handle None values
        'address': row[5],
        'aadhar_number': row[6],
        'mobile_number': row[7],
        'alternate_mobile': row[8] or '',  # Handle None values
        'gender': row[9] or '',  # Handle None values
        'children_count': row[10] or 0,  # Handle None values
        'amount_paid_today': row[11],
        'remaining_amount': row[12],
        'check_in_done': row[13],
        'room_number': row[14],
        'check_in_date': row[15],
        'check_out_date': row[16] or '',  # Handle None values
        'check_out_time': row[17] or '',  # Handle None values
        'extra_bed': row[18] or False,  # Handle None values
        'recipe_number': row[19] or '',  # Handle None values
        'comments': row[20] or '',  # Handle None values
        'created_at': row[21],
        'payment_mode': row[22] or 'Cash',  # Handle None values
        'receipt_generated': False,  # Not in current schema
        'receipt_generated_date': '',  # Not in current schema
        'receipt_generated_by': '',  # Not in current schema
        'receipt_number': row[19] or ''  # Use recipe_number
    }
    
    return render_template('edit_tourist_profile.html', tourist=tourist)

@app.route('/tourist_profile/<int:tourist_id>/delete', methods=['POST'])
def delete_tourist_profile(tourist_id):
    """Delete a tourist profile"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Get tourist name before deletion
        cursor.execute('SELECT full_name FROM tourists WHERE id = ?', (tourist_id,))
        result = cursor.fetchone()
        
        if result:
            tourist_name = result[0]
            cursor.execute('DELETE FROM tourists WHERE id = ?', (tourist_id,))
            conn.commit()
            flash(f'Tourist profile for {tourist_name} has been deleted successfully!', 'success')
        else:
            flash('Tourist profile not found', 'error')
            
    except Exception as e:
        flash(f'Error deleting profile: {str(e)}', 'error')
    
    conn.close()
    return redirect(url_for('tourist_profiles'))

@app.route('/generate_receipt/<int:tourist_id>', methods=['POST'])
def generate_receipt(tourist_id):
    """Generate receipt for a tourist (only if check-in is completed)"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get tourist data
        tourist_data = get_tourist_full_data(tourist_id)
        if not tourist_data:
            flash('Tourist not found', 'error')
            return redirect(url_for('index'))
        
        # Check if check-in is completed
        if not tourist_data.get('check_in_done'):
            flash('Receipt can only be generated after check-in is completed', 'error')
            return redirect(url_for('index'))
        
        # Generate receipt with number - this returns a tuple
        receipt_result = generate_receipt_with_number(tourist_id, session.get('username', 'admin'))
        
        if receipt_result[0] is None:
            # Error occurred
            flash(f'Error generating receipt: {receipt_result[1]}', 'error')
            return redirect(url_for('index'))
        
        receipt_number = receipt_result[0]
        message = receipt_result[1]
        
        # Generate custom Hindi receipt PDF
        pdf_path = generate_custom_hindi_receipt(tourist_data, receipt_number)
        
        # Store PDF path in session for download
        session['latest_receipt'] = pdf_path
        
        flash(f'Receipt #{receipt_number} generated successfully!', 'success')
        
    except Exception as e:
        flash(f'Error generating receipt: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/download_custom_receipt/<int:tourist_id>')
def download_custom_receipt(tourist_id):
    """Download custom Hindi receipt for a tourist (only if check-in is completed)"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        print(f"🔍 Download request for tourist_id: {tourist_id}")
        
        # Get tourist data using simple SQL query
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT full_name, recipe_number, check_in_done 
            FROM tourists WHERE id = ?
        ''', (tourist_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            flash('Tourist not found', 'error')
            return redirect(url_for('index'))
        
        full_name, recipe_number, check_in_done = result
        print(f"✅ Tourist: {full_name}")
        
        # Check if check-in is completed
        if not check_in_done:
            flash('Receipt can only be downloaded after check-in is completed', 'error')
            return redirect(url_for('index'))
        
        # Get receipt number
        final_receipt_number = recipe_number
        if not final_receipt_number:
            flash('No receipt generated for this tourist', 'error')
            return redirect(url_for('index'))
        
        print(f"📄 Receipt number: {final_receipt_number}")
        
        # Get full tourist data for PDF generation
        tourist_data = get_tourist_full_data(tourist_id)
        if not tourist_data:
            flash('Error retrieving tourist data', 'error')
            return redirect(url_for('index'))
        
        # Generate custom Hindi receipt PDF
        pdf_path = generate_custom_hindi_receipt(tourist_data, final_receipt_number)
        
        if pdf_path and os.path.exists(pdf_path):
            print(f"✅ PDF generated successfully: {pdf_path}")
            return send_file(pdf_path, as_attachment=True, 
                           download_name=f'receipt_{final_receipt_number}.pdf')
        else:
            print(f"❌ Failed to generate PDF")
            flash('Error generating receipt PDF', 'error')
            return redirect(url_for('index'))
        
    except Exception as e:
        print(f"❌ Download error: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error downloading receipt: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/search_tourists', methods=['GET', 'POST'])
def search_tourists_route():
    """Search and filter tourists"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    results = []
    search_params = {}
    
    if request.method == 'POST':
        search_params = {
            'name': request.form.get('name', '').strip(),
            'aadhar': request.form.get('aadhar', '').strip(),
            'mobile': request.form.get('mobile', '').strip(),
            'receipt_number': request.form.get('receipt_number', '').strip(),
            'date': request.form.get('date', '').strip(),
            'date_from': request.form.get('date_from', '').strip(),
            'date_to': request.form.get('date_to', '').strip(),
            'receipt_issued': request.form.get('receipt_issued', '').strip()
        }
        
        try:
            results = search_tourists(search_params)
        except Exception as e:
            flash(f'Error searching tourists: {str(e)}', 'error')
    
    return render_template('search_tourists.html', results=results, search_params=search_params)

@app.route('/api/tourist_details/<int:tourist_id>')
def get_tourist_details_api(tourist_id):
    """API endpoint to get tourist details"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        tourist_data = get_tourist_full_data(tourist_id)
        if tourist_data:
            return jsonify(tourist_data)
        else:
            return jsonify({'error': 'Tourist not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_receipt/<int:tourist_id>')
def download_receipt_by_id(tourist_id):
    """Download receipt for a specific tourist"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get tourist data using the proper function
        tourist_data = get_tourist_full_data(tourist_id)
        
        if not tourist_data:
            flash('Tourist not found', 'error')
            return redirect(url_for('index'))
        
        # Check if tourist has a receipt number
        recipe_number = tourist_data.get('recipe_number')
        if not recipe_number:
            flash('No receipt available for this guest', 'error')
            return redirect(url_for('index'))
        
        # Generate PDF using the receipt number
        pdf_file_path = generate_custom_hindi_receipt(tourist_data, recipe_number)
        
        # Ensure we have a valid file path string
        if pdf_file_path and isinstance(pdf_file_path, str) and os.path.exists(pdf_file_path):
            return send_file(pdf_file_path, as_attachment=True, 
                           download_name=f'receipt_{recipe_number}.pdf')
        else:
            flash('Error generating receipt PDF', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f'Error downloading receipt: {str(e)}', 'error')
        return redirect(url_for('index'))

def generate_receipt_number():
    """Generate a unique receipt number"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Get the current date for the receipt number prefix
        today = datetime.now()
        date_prefix = today.strftime('%Y%m%d')  # Format: YYYYMMDD
        
        # Find the highest receipt number for today
        cursor.execute('''
            SELECT recipe_number FROM tourists 
            WHERE recipe_number LIKE ? 
            ORDER BY recipe_number DESC 
            LIMIT 1
        ''', (f'RCP{date_prefix}%',))
        
        result = cursor.fetchone()
        
        if result:
            # Extract the sequence number from the last receipt
            last_receipt = result[0]
            try:
                # Extract the last 4 digits (sequence number)
                last_sequence = int(last_receipt[-4:])
                new_sequence = last_sequence + 1
            except (ValueError, IndexError):
                # If parsing fails, start from 1
                new_sequence = 1
        else:
            # No receipts for today, start from 1
            new_sequence = 1
        
        # Generate the new receipt number: RCP + YYYYMMDD + 4-digit sequence
        receipt_number = f'RCP{date_prefix}{new_sequence:04d}'
        
        # Verify the receipt number is unique (just in case)
        cursor.execute('SELECT COUNT(*) FROM tourists WHERE recipe_number = ?', (receipt_number,))
        if cursor.fetchone()[0] > 0:
            # If somehow it exists, try with a random suffix
            import random
            receipt_number = f'RCP{date_prefix}{new_sequence:04d}{random.randint(10,99)}'
        
        conn.close()
        return receipt_number
        
    except Exception as e:
        print(f"Error generating receipt number: {e}")
        # Fallback: use timestamp-based receipt number
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        conn.close()
        return f'RCP{timestamp}'

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    
    # Run the Flask application
    print("🏨 Aggarwal Bhawan Management System Starting...")
    print("📊 Total Rooms: 157")
    print("🌐 Access URL: http://localhost:5000")
    print("👤 Default Login: admin / admin123")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
