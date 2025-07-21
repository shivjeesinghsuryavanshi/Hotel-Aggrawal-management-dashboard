# 🏨 HOTEL RECEIPT FORMAT - CODE BREAKDOWN

## 📋 Section-by-Section Code Analysis

### 1. 🎨 HEADER SECTION (Navy Blue Background)
```python
# Lines 113-125: Header background and title
c.setFillColor(colors.navy)
c.rect(0, height-100, width, 100, fill=1, stroke=0)

c.setFillColor(colors.white)
c.setFont("Helvetica-Bold", 26)
c.drawCentredString(width/2, height-40, "🏨 HOTEL RECEIPT 🏨")
c.setFont("Helvetica", 14)
c.drawCentredString(width/2, height-65, "Hotel Management System")
c.setFont("Helvetica", 10)
c.drawCentredString(width/2, height-85, "★★★★ Premium Hotel Services ★★★★")
```

### 2. 📊 RECEIPT NUMBER & DATE BOXES
```python
# Lines 127-143: Receipt number box (Left side)
c.setFillColor(colors.lightgrey)
c.setStrokeColor(colors.black)
c.rect(50, height-150, 150, 40, fill=1, stroke=1)
c.setFillColor(colors.black)
c.setFont("Helvetica-Bold", 12)
c.drawCentredString(125, height-135, f"Receipt No:")
c.setFont("Helvetica-Bold", 14)
c.drawCentredString(125, height-155, f"{receipt_number}")

# Lines 145-153: Date box (Right side)
c.setFillColor(colors.lightgrey)
c.rect(width-200, height-150, 150, 40, fill=1, stroke=1)
c.setFillColor(colors.black)
c.setFont("Helvetica-Bold", 12)
current_date = datetime.now().strftime('%d/%m/%Y %I:%M %p')
c.drawCentredString(width-125, height-135, f"Date:")
c.setFont("Helvetica-Bold", 14)
c.drawCentredString(width-125, height-155, f"{current_date}")
```

### 3. 👤 GUEST DETAILS SECTION
```python
# Lines 155-185: Guest details section
y_pos = height - 200
c.setFillColor(colors.darkblue)
c.setFont("Helvetica-Bold", 16)
c.drawString(50, y_pos, "GUEST DETAILS")

# Guest details box
c.setFillColor(colors.white)
c.setStrokeColor(colors.grey)
c.rect(50, y_pos-160, width-100, 150, fill=1, stroke=1)

y_pos -= 25
c.setFillColor(colors.black)
c.setFont("Helvetica", 12)

# Guest information fields
guest_name = tourist_data.get('full_name', '')
c.drawString(60, y_pos, f"Name: {guest_name}")
y_pos -= 20

father_spouse = tourist_data.get('father_spouse_name', '')
if father_spouse:
    c.drawString(60, y_pos, f"S/o, W/o: {father_spouse}")
    y_pos -= 20

address = tourist_data.get('address', '')
c.drawString(60, y_pos, f"Address: {address}")
y_pos -= 20

mobile = tourist_data.get('mobile_number', '')
aadhar = tourist_data.get('aadhar_number', '')
c.drawString(60, y_pos, f"Mobile: {mobile}")
c.drawString(350, y_pos, f"Aadhar: {aadhar}")
```

### 4. 🏠 STAY DETAILS SECTION
```python
# Lines 187-213: Stay details section
c.setFillColor(colors.darkblue)
c.setFont("Helvetica-Bold", 16)
c.drawString(50, y_pos, "STAY DETAILS")

# Stay details box
c.setFillColor(colors.white)
c.rect(50, y_pos-120, width-100, 110, fill=1, stroke=1)

y_pos -= 25
c.setFillColor(colors.black)
c.setFont("Helvetica", 12)

# Room and bed information
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
```

### 5. 💰 PAYMENT DETAILS TABLE
```python
# Lines 215-278: Payment details section
c.setFillColor(colors.darkblue)
c.setFont("Helvetica-Bold", 16)
c.drawString(50, y_pos, "PAYMENT DETAILS")

# Payment table setup
y_pos -= 25
table_x = 50
table_y = y_pos - 20
col_widths = [300, 150]  # Description: 300px, Amount: 150px
row_height = 30

# Table header
c.setFillColor(colors.lightgrey)
c.setStrokeColor(colors.black)
c.rect(table_x, table_y, col_widths[0], row_height, fill=1, stroke=1)
c.rect(table_x + col_widths[0], table_y, col_widths[1], row_height, fill=1, stroke=1)

c.setFillColor(colors.black)
c.setFont("Helvetica-Bold", 12)
c.drawCentredString(table_x + col_widths[0]/2, table_y + 10, "Description")
c.drawCentredString(table_x + col_widths[0] + col_widths[1]/2, table_y + 10, "Amount")

# Payment rows
payments = [
    ("Amount Paid Today", float(tourist_data.get('amount_paid_today', 0))),
    ("Remaining Amount", float(tourist_data.get('remaining_amount', 0))),
]

for i, (description, amount) in enumerate(payments):
    row_y = table_y - (i + 1) * row_height
    
    # Alternate row colors
    if i % 2 == 0:
        c.setFillColor(colors.white)
    else:
        c.setFillColor(colors.lightgrey)
    
    c.rect(table_x, row_y, col_widths[0], row_height, fill=1, stroke=1)
    c.rect(table_x + col_widths[0], row_y, col_widths[1], row_height, fill=1, stroke=1)
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    c.drawString(table_x + 10, row_y + 10, description)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(table_x + col_widths[0] + 10, row_y + 10, f"₹ {amount:.2f}")

# Total amount box (Navy blue background)
total_amount = float(tourist_data.get('amount_paid_today', 0)) + float(tourist_data.get('remaining_amount', 0))
y_pos -= 120

c.setFillColor(colors.navy)
c.rect(table_x + col_widths[0], y_pos, col_widths[1], 50, fill=1, stroke=1)
c.setFillColor(colors.white)
c.setFont("Helvetica-Bold", 16)
c.drawCentredString(table_x + col_widths[0] + col_widths[1]/2, y_pos + 25, f"Total:")
c.drawCentredString(table_x + col_widths[0] + col_widths[1]/2, y_pos + 10, f"₹ {total_amount:.2f}")
```

### 6. 📋 TERMS & CONDITIONS SECTION
```python
# Lines 290-310: Terms and conditions
y_pos -= 100
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
```

### 7. 🙏 FOOTER SECTION (Navy Blue Background)
```python
# Lines 312-340: Footer section
y_pos -= 120
c.setFillColor(colors.navy)
c.rect(0, 0, width, 150, fill=1, stroke=0)

c.setFillColor(colors.white)
c.setFont("Helvetica-Bold", 16)
c.drawCentredString(width/2, y_pos + 80, "Thank You for Staying with Us!")
c.setFont("Helvetica", 14)
c.drawCentredString(width/2, y_pos + 60, "We hope you had a pleasant stay!")

# Signature areas
c.setFont("Helvetica", 12)
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
```

## 🔧 CUSTOMIZATION AREAS

### Colors (Easy to Change):
- `colors.navy` → Header/Footer background
- `colors.darkblue` → Section headers
- `colors.lightgrey` → Info boxes
- `colors.white` → Content areas
- `colors.black` → Text

### Fonts (Easy to Change):
- `Helvetica-Bold` → Headers and important text
- `Helvetica` → Regular text
- Font sizes: 26, 16, 14, 12, 11, 10, 8

### Positioning (Coordinate System):
- `height-100` → Header position
- `width/2` → Center alignment
- `50, y_pos` → Left margin
- `width-100` → Right margin with padding

### Data Fields (From Database):
- `tourist_data.get('full_name', '')`
- `tourist_data.get('mobile_number', '')`
- `tourist_data.get('amount_paid_today', 0)`
- All other tourist_data fields

This format creates a professional, structured receipt with clear sections and consistent styling!
