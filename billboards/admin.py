from django.contrib import admin
from django.http import HttpResponse
from .models import Billboard, Booking
from reportlab.pdfgen import canvas
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
import io
from datetime import date

@admin.action(description='Download Available Boards PDF')
def download_availability_pdf(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="available_billboards.pdf"'
    
    p = canvas.Canvas(response)
    p.setTitle("Skyview Availability Report")
    
    # Header
    p.setFont("Helvetica-Bold", 20)
    p.setFillColorRGB(0.04, 0.14, 0.25) # Navy
    p.drawString(50, 800, "SKYVIEW BILLBOARDS")
    
    p.setFont("Helvetica", 12)
    p.setFillColorRGB(0.4, 0.4, 0.4)
    p.drawString(50, 780, f"Availability Report - {date.today().strftime('%d %B %Y')}")
    
    p.setStrokeColorRGB(0, 0.83, 1) # Cyan
    p.line(50, 770, 545, 770)
    
    y = 740
    # Filter only available boards
    available_boards = queryset.filter(is_available=True)
    
    if not available_boards.exists():
        p.setFont("Helvetica", 12)
        p.setFillColorRGB(0, 0, 0)
        p.drawString(50, y, "No available billboards found at this time.")
    else:
        for board in available_boards:
            if y < 180: # Check if space for next item (image + text)
                p.showPage()
                y = 800
                p.setFont("Helvetica-Bold", 10)
                p.setFillColorRGB(0, 0.83, 1)
                p.drawString(50, 820, "SKYVIEW BILLBOARDS (cont.)")
                p.line(50, 815, 545, 815)
                
            p.setFont("Helvetica-Bold", 14)
            p.setFillColorRGB(0.04, 0.14, 0.25)
            p.drawString(50, y, board.title)
            
            p.setFont("Helvetica-Bold", 12)
            p.setFillColorRGB(0, 0.83, 1) # Cyan
            p.drawRightString(545, y, f"₹{board.price_per_month}/mo")
            
            p.setFont("Helvetica", 10)
            p.setFillColorRGB(0, 0, 0)
            p.drawString(50, y-15, f"Location: {board.location}")
            p.drawString(50, y-28, f"Size: {board.size} | Total Area: {board.sqft} sqft")
            
            # Description (truncated)
            desc = board.description[:100] + "..." if len(board.description) > 100 else board.description
            p.setFont("Helvetica-Oblique", 9)
            p.setFillColorRGB(0.3, 0.3, 0.3)
            p.drawString(50, y-42, desc)
            
            # Image
            if board.image:
                try:
                    # Draw image at 50, y-130
                    p.drawImage(board.image.path, 50, y-130, width=150, height=80, preserveAspectRatio=True)
                except Exception as e:
                    p.setFont("Helvetica", 8)
                    p.drawString(50, y-60, f"[Image load error]")
            
            y -= 160 # Space for next item
            p.setStrokeColorRGB(0.9, 0.9, 0.9)
            p.line(50, y+15, 545, y+15)
            y -= 10
            
    p.save()
    return response

@admin.action(description='Download Invoice PDF')
def download_invoice_pdf(modeladmin, request, queryset):
    # Simplification: Generate one PDF for the first selected item, or zip? 
    # Let's just do the first one for the demo or iterate if browser handles multiple downloads (it doesn't usually).
    # We will loop and return the last one, or just error if multiple.
    booking = queryset.first()
    if not booking:
        return
        
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{booking.id}.pdf"'
    
    p = canvas.Canvas(response)
    width, height = 595.27, 841.89 # A4 size
    
    # --- HEADER ---
    # Left: Address
    p.setFont("Helvetica-Bold", 16)
    p.setFillColorRGB(0.8, 0, 0) # Red color for logo
    p.drawString(40, 800, "SKY VIEW")
    
    p.setFont("Helvetica", 8)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(40, 785, "12/454 ARPOOKARA, VILLOONNI-686008")
    p.drawString(40, 775, "KOTTAYAM, skyview330@gmail.com")
    p.setFont("Helvetica-Bold", 9)
    p.drawString(40, 760, "Ph; 9447266404, 9495806837")
    
    # Right: Tax Details
    p.setFont("Helvetica", 8)
    p.drawString(350, 800, "HSN: 9989")
    p.drawString(350, 790, "GSTIN: 32AHFPT0757R1ZR")
    p.drawString(350, 780, "PAN: AHFPT0757R")
    p.drawString(350, 770, "GST-REG: 32AHFPT0757R1ZR")
    
    # Center: TAX-INVOICE
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(width/2, 750, "TAX-INVOICE")
    
    # --- BILL TO PARTY ---
    y_bill = 720
    p.setFont("Helvetica-Bold", 9)
    p.drawString(40, y_bill, "BILL TO PARTY")
    p.setFont("Helvetica", 9)
    p.drawString(40, y_bill-12, f"{booking.customer_name}")
    p.drawString(40, y_bill-24, f"{booking.customer_email}") # Using email as address placeholder
    p.drawString(40, y_bill-36, f"Ph: {booking.customer_phone}")
    
    # --- INVOICE BAR ---
    p.rect(30, 660, 535, 20) # Box
    p.setFont("Helvetica-Bold", 9)
    p.drawString(40, 666, f"Your Order/Ref No: 20-9-25/{booking.id}")
    p.drawString(250, 666, f"Invoice No: {booking.id}")
    p.drawString(450, 666, f"Date: {booking.created_at.strftime('%d/%m/%Y')}")
    
    # --- TABLE HEADER ---
    y_table = 630
    p.rect(30, 300, 535, 360) # Main Box (from 660 down to 300)
    p.line(30, y_table, 565, y_table) # Header line logic is tricky with rect, drawing manual line
    # Actually let's draw headers inside the big box
    p.line(30, 640, 565, 640) # Header bottom line
    
    # Vertical lines
    p.line(60, 660, 60, 350) # Sl No line
    p.line(460, 660, 460, 300) # Amount column line
    p.line(510, 640, 510, 300) # Rs/Ps split
    
    p.setFont("Helvetica-Bold", 9)
    p.drawString(35, 645, "Sl No")
    p.drawCentredString(260, 645, "PARTICULARS")
    p.drawCentredString(500, 650, "Amount")
    p.drawString(480, 632, "Rs")
    p.drawString(530, 632, "Ps")
    
    # --- TABLE CONTENT ---
    y_row = 620
    p.setFont("Helvetica", 9)
    p.drawString(35, y_row, "1.")
    
    p.setFont("Helvetica-Bold", 9)
    p.drawString(70, y_row, "Advertisement of the Hoarding")
    
    p.setFont("Helvetica", 9)
    y_det = y_row - 15
    p.drawString(70, y_det, "Location")
    p.drawString(200, y_det, f": {booking.billboard.location}")
    y_det -= 12
    p.drawString(70, y_det, "Display")
    p.drawString(200, y_det, f": {booking.customer_name}")
    y_det -= 12
    p.drawString(70, y_det, "Hoarding Size")
    p.drawString(200, y_det, f": {booking.billboard.size}")
    y_det -= 12
    p.drawString(70, y_det, "Total Area")
    p.drawString(200, y_det, f": {booking.billboard.sqft} Sq. Ft")
    y_det -= 12
    p.drawString(70, y_det, "Duration")
    p.drawString(200, y_det, f": {booking.duration_months} Months")
    
    # Date Range (approx)
    from datetime import timedelta
    end_date = booking.start_date + timedelta(days=30*booking.duration_months)
    y_det -= 20
    p.drawString(70, y_det, f"({booking.start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')})")
    
    # Calculations
    # Assuming total_amount in DB is the Grand Total (incl tax).
    # Base = Total / 1.18
    # CGST = Base * 0.09
    # SGST = Base * 0.09
    
    try:
        grand_total = float(booking.total_amount)
        base_amount = grand_total / 1.18
        tax_amount = base_amount * 0.09
        
        # Rounding
        base_amount_str = f"{base_amount:.2f}"
        tax_str = f"{tax_amount:.2f}"
        total_str = f"{grand_total:.2f}"
        
        base_rs, base_ps = base_amount_str.split('.')
        tax_rs, tax_ps = tax_str.split('.')
        tot_rs, tot_ps = total_str.split('.')
        
    except:
        base_rs, base_ps = "0", "00"
        tax_rs, tax_ps = "0", "00"
        tot_rs, tot_ps = "0", "00"
    
    # Amounts
    y_amt = 400
    p.setFont("Helvetica-Bold", 9)
    p.drawRightString(455, y_amt, f"{booking.duration_months} months Amount")
    p.setFont("Helvetica", 9)
    p.drawRightString(505, y_amt, base_rs)
    p.drawRightString(560, y_amt, base_ps)
    
    y_amt -= 20
    p.setFont("Helvetica-Bold", 9)
    p.drawRightString(455, y_amt, "CGST (9%)")
    p.setFont("Helvetica", 9)
    p.drawRightString(505, y_amt, tax_rs)
    p.drawRightString(560, y_amt, tax_ps)
    
    y_amt -= 15
    p.setFont("Helvetica-Bold", 9)
    p.drawRightString(455, y_amt, "SGST (9%)")
    p.setFont("Helvetica", 9)
    p.drawRightString(505, y_amt, tax_rs)
    p.drawRightString(560, y_amt, tax_ps)
    
    # Total Line
    p.line(30, 350, 565, 350)
    p.setFont("Helvetica-Bold", 10)
    p.drawRightString(455, 335, "GRAND TOTAL")
    p.drawRightString(505, 335, tot_rs)
    p.drawRightString(560, 335, tot_ps)
    
    # Words
    p.rect(30, 275, 535, 25)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(40, 282, "Rupees in word:")
    p.setFont("Helvetica", 9)
    p.drawString(130, 282, f"Total Amount Only.") # Placeholder for num2words
    
    # Image in table (small)
    if booking.billboard.image:
        try:
             p.drawImage(booking.billboard.image.path, 350, 480, width=100, height=80, preserveAspectRatio=True)
        except:
             pass

    # Footer
    p.setFont("Helvetica", 7)
    p.drawString(40, 250, "All payment should be strictly made by cash/draft/cheque favoring 'SKY VIEW'.")
    
    # Signature
    p.setFont("Helvetica-Bold", 9)
    p.drawString(400, 240, "Authorised Signatory")
    p.drawString(400, 230, "For Sky View")
    
    p.save()
    return response

@admin.action(description='Send Invoice via Email')
def send_invoice_email(modeladmin, request, queryset):
    count = 0
    for booking in queryset:
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 800, f"INVOICE #{booking.id}")
        p.drawString(100, 780, f"Customer: {booking.customer_name}")
        p.drawString(100, 760, f"Billboard: {booking.billboard.title}")
        
        if booking.billboard.image:
            try:
                img_path = booking.billboard.image.path
                p.drawImage(img_path, 100, 500, width=200, height=150, preserveAspectRatio=True)
            except:
                pass
                
        p.drawString(100, 400, f"Total: {booking.total_amount}")
        p.save()
        pdf = buffer.getvalue()
        buffer.close()
        
        email = EmailMessage(
            f'Invoice for Booking #{booking.id}',
            'Please find attached your invoice from Skyview Billboards.',
            'skyview230@gmail.com',
            [booking.customer_email],
        )
        email.attach(f'invoice_{booking.id}.pdf', pdf, 'application/pdf')
        try:
            email.send(fail_silently=False)
            count += 1
        except Exception as e:
            modeladmin.message_user(request, f"Failed to send to {booking.customer_email}: {e}", level='error')
            
    modeladmin.message_user(request, f"{count} emails sent successfully.")

class BillboardAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'is_available', 'sqft', 'price_per_month')
    list_filter = ('is_available',)
    actions = [download_availability_pdf]

class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'billboard', 'total_amount', 'created_at')
    actions = [download_invoice_pdf, send_invoice_email]

admin.site.register(Billboard, BillboardAdmin)
admin.site.register(Booking, BookingAdmin)

# Unregister default User admin and register custom one to hide 'last_login' if that's the concern
class CustomUserAdmin(UserAdmin):
    # Default list_display is ('username', 'email', 'first_name', 'last_name', 'is_staff', 'last_login')
    # We remove 'last_login'
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

try:
    admin.site.unregister(User)
    admin.site.register(User, CustomUserAdmin)
except admin.sites.NotRegistered:
    pass
