from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import logging
import requests
import qrcode
from io import BytesIO
import base64
from flask_mail import Mail, Message
from datetime import datetime 
from flask import send_from_directory

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'eye2k25@gmail.com'
app.config['MAIL_PASSWORD'] = 'ykro ugjv gbsp fqyu'
mail = Mail(app)

# SheetsDB API Endpoints
TECHNICAL_SHEETDB_URL = "https://sheetdb.io/api/v1/jcin7xzlvn7ss"  # For technical events
NON_TECHNICAL_SHEETDB_URL = "https://sheetdb.io/api/v1/rdn5i9dzptwbr"  # For non-technical events

# Fest events and their fees with category
FEST_EVENTS = {
    # Technical Events
    "Project Expo": {"fee": 300, "category": "technical"},
    "Hackathon": {"fee": 300, "category": "technical"},
    "Poster or Paper Presentation": {"fee": 300, "category": "technical"},
    "Technical Quiz": {"fee": 1000, "category": "technical"},
    "Circuit Hunt": {"fee": 300, "category": "technical"},
    "Workshop": {"fee": 500, "category": "technical"},
    
    # Non-Technical Events
    "Chess": {"fee": 50, "category": "non-technical"},
    "Fastest Fingers First": {"fee": 75, "category": "non-technical"},
    "Photography": {"fee": 50, "category": "non-technical"},
    "Drawing": {"fee": 50, "category": "non-technical"},
    "MEME": {"fee": 50, "category": "non-technical"},
    "Free Fire": {"fee": 200, "category": "non-technical"}
}
@app.route('/googlexxxxx.html')
def serve_verification_file():
    return send_from_directory('.', 'google12132244958a9137.html')

VISITOR_FILE = "visitors.txt"

def load_visitor_count():
    """Load the visitor count from the file."""
    if os.path.exists(VISITOR_FILE):
        with open(VISITOR_FILE, "r") as file:
            return int(file.read().strip())
    return 0  # Default if file doesn't exist

def save_visitor_count(count):
    """Save the visitor count to the file."""
    with open(VISITOR_FILE, "w") as file:
        file.write(str(count))

# Load visitor count on server start
visitor_count = load_visitor_count()

@app.route('/')
def home():
    global visitor_count
    visitor_count += 1  # Increment count
    save_visitor_count(visitor_count)  # Save to file
    return render_template('home.html', visitor_count=visitor_count)

@app.route('/events')
def events():
    return render_template('events.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/contactus')
def contactus():
    return render_template('contactus.html')

@app.route('/terms_and_conditions')
def terms_and_conditions():
    return render_template('terms_and_conditions.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        try:
            registration_data = {
                'fullname': request.form['fullname'],
                'email': request.form['email'],
                'mobile': request.form['mobile'],
                'yourcollege': request.form['yourcollege'],
                'event_name': request.form['event'],
            }

            if registration_data['event_name'] not in FEST_EVENTS:
                flash("Invalid event selected.", "error")
                return redirect(url_for('registration'))

            event_info = FEST_EVENTS[registration_data['event_name']]
            registration_data['event_fee'] = event_info['fee']
            registration_data['event_category'] = event_info['category']
            session['registration_data'] = registration_data

            return redirect(url_for('payment'))
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            flash("An error occurred. Please try again.", "error")
            return redirect(url_for('registration'))

    # Get the selected event from query parameters
    selected_event = request.args.get('event')
    event_fee = FEST_EVENTS.get(selected_event, {}).get('fee', 0) if selected_event else 0

    return render_template('registration.html', 
                         selected_event=selected_event,
                         event_fee=event_fee,
                         festevents=FEST_EVENTS)

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    registration_data = session.get('registration_data')
    if not registration_data:
        flash("Please complete registration first.", "error")
        return redirect(url_for('registration'))
    
    if request.method == 'POST':
        return redirect(url_for('qr_code'))

    return render_template('payment.html', registration_data=registration_data)


@app.route('/qr_code')
def qr_code():
    registration_data = session.get('registration_data')
    if not registration_data:
        flash("Please complete registration first.", "error")
        return redirect(url_for('registration'))
    
    return render_template('qr_code.html', registration_data=registration_data)

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    try:
        registration_data = session.get('registration_data')
        if not registration_data:
            return jsonify({"error": "Registration data not found"}), 400

        event_fee = registration_data['event_fee']
        upi_link = f"upi://pay?pa=sunilreddyyaparla-1@okicici&pn=EYE2K25&am={event_fee}&cu=INR"

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(upi_link)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()

        return jsonify({"qr_code": qr_base64, "upi_link": upi_link})

    except Exception as e:
        logger.error(f"QR Code generation failed: {str(e)}")
        return jsonify({"error": "Failed to generate QR Code"}), 500

@app.route('/submit_transaction', methods=['POST'])
def submit_transaction():
    try:
        registration_data = session.get('registration_data')
        if not registration_data:
            return jsonify({"status": "error", "message": "Registration data not found"}), 400

        # Create transaction data
        transaction_data = {
            "name": registration_data['fullname'],
            "email": registration_data['email'],
            "mobile": registration_data['mobile'],
            "college": registration_data['yourcollege'],
            "event": registration_data['event_name'],
            "amount": registration_data['event_fee'],
            "payment_app": request.form.get('payment_app'),
            "other_upi_app": request.form.get('other_upi_app') if request.form.get('payment_app') == 'Other UPI' else '',
            "upi_reference": request.form.get('upi_reference'),
            "payment_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Select the appropriate SheetDB URL based on event category
        if registration_data['event_category'] == 'technical':
            sheetdb_url = TECHNICAL_SHEETDB_URL
            logger.debug(f"Using Technical SheetDB URL for {registration_data['event_name']}")
        else:
            sheetdb_url = NON_TECHNICAL_SHEETDB_URL
            logger.debug(f"Using Non-Technical SheetDB URL for {registration_data['event_name']}")

        # Test API connection first
        try:
            # Log the exact data being sent
            logger.debug(f"Sending data to SheetDB ({registration_data['event_category']}): {transaction_data}")
            
            # Make the API request with extended timeout and error handling
            response = requests.post(
                sheetdb_url, 
                json={"data": [transaction_data]}, 
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            # Log the complete response
            logger.debug(f"SheetDB Response Status: {response.status_code}")
            logger.debug(f"SheetDB Response Headers: {response.headers}")
            logger.debug(f"SheetDB Response Content: {response.text}")

            if response.status_code == 201:
                # Success case
                try:
                    send_confirmation_email(transaction_data)
                except Exception as email_error:
                    logger.error(f"Email sending failed but payment recorded: {str(email_error)}")
                
                session.clear()
                return jsonify({
                    "status": "success",
                    "message": "Payment recorded successfully!"
                })
            else:
                # Log detailed error information
                error_message = f"SheetDB Error: Status {response.status_code}"
                try:
                    error_details = response.json()
                    error_message += f", Details: {error_details}"
                except:
                    error_message += f", Response: {response.text}"
                
                logger.error(error_message)
                return jsonify({
                    "status": "error",
                    "message": "Failed to record payment. Please contact support.",
                    "debug_info": error_message
                }), 500

        except requests.exceptions.Timeout:
            logger.error("SheetDB API timeout")
            return jsonify({
                "status": "error",
                "message": "Connection timeout. Please try again."
            }), 504

        except requests.exceptions.RequestException as e:
            logger.error(f"SheetDB API request failed: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Connection to payment server failed. Please try again."
            }), 500

    except Exception as e:
        logger.error(f"Transaction processing error: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred. Please try again."
        }), 500

def send_confirmation_email(transaction_data):
    try:
        msg = Message(
            'EYE 2K25 Registration Confirmation',
            sender=app.config['MAIL_USERNAME'],
            recipients=[transaction_data['email']]
        )
        msg.body = f"""
Dear {transaction_data['name']},

🎉 Thank you for registering for EYE 2K25! We are thrilled to have you join us for this exciting event.

Here are your registration details:
--------------------------------------------------
📌 Event:{transaction_data['event']}
💰 Amount Paid:₹{transaction_data['amount']}
🆔 Transaction ID:{transaction_data['upi_reference']}
🏫 College:{transaction_data['college']}
📅 Registration Time:{transaction_data['payment_time']}
--------------------------------------------------

Next Steps:
✅ Please keep this email as proof of registration.
✅ On the event day, bring a valid student ID for verification.
✅ Stay tuned for event updates via email and our official website.

🔗 Visit our website: [www.eye2k25.in] 
📧 Need assistance? Reply to this email or contact us.  

We can't wait to see you at EYE 2K25!  

---
Best regards, 
📍 The EYE 2K25 Team
"""
        mail.send(msg)
        logger.info("Confirmation email sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}", exc_info=True)


@app.route('/pay_success')
def payment_success():
    return render_template('pay_success.html')

@app.route('/payment_failure')
def payment_failure():
    return render_template('payment_fail.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
