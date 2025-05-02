from flask import Flask, render_template, request, redirect, url_for, session
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key')  # Use env variable in production

# Simulated database (replace with SQLite/MySQL in production)
admissions = []
approved_students = []

# Hardcoded admin password (replace with hashed passwords in production)
ADMIN_PASSWORD = 'Asraful158'  # Change to a secure password

# Email configuration (use environment variables in production)
SENDER_EMAIL = 'ourcoaching6@gmail.com'
SENDER_PASSWORD = 'ufoi fbik vooj vepn'  # WARNING: Do not hardcode in production

# Generate random passkey for approved students
def generate_passkey():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Function to send email with passkey
def send_passkey_email(recipient_email, passkey, student_name):
    try:
        # Set up the MIME
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = 'Your Exam Passkey for Re-start Coaching Center'

        # Email body
        body = f"""
        Dear {student_name},

        Congratulations! Your admission application has been approved.
        Your unique exam passkey is: {passkey}

        Please use this passkey to access the exam at our website.
        If you have any questions, contact us at {SENDER_EMAIL}.

        Best regards,
        Re-start Coaching Center
        """
        msg.attach(MIMEText(body, 'plain'))

        # Connect to Gmail's SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Enable TLS
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        print(f"Email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {recipient_email}: {e}")
        return False

# Home route with teacher data for slideshow
@app.route('/')
def home():
    teachers = [
        {'img': url_for('static', filename='images/teacher1.jpg'), 'name': 'Sheikh Asraful'},
        {'img': url_for('static', filename='images/teacher2.jpg'), 'name': 'Sarjis Alam'},
        {'img': url_for('static', filename='images/teacher3.jpg'), 'name': 'kkkr Alam'},
        {'img': url_for('static', filename='images/teacher4.jpg'), 'name': 'Jonker Ali'},
        {'img': url_for('static', filename='images/teacher5.jpg'), 'name': 'Hasnat Khan'}
    ]
    return render_template('index.html', teachers=teachers)

# Admission form route
@app.route('/admission', methods=['GET', 'POST'])
def admission():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        admissions.append({'name': name, 'email': email, 'phone': phone, 'status': 'pending'})
        return redirect(url_for('home'))
    return render_template('admission.html')

# Admin login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error="Invalid password")
    return render_template('login.html', error=None)

# Admin panel route
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        email = request.form['email']
        action = request.form['action']
        for student in admissions:
            if student['email'] == email:
                if action == 'approve':
                    passkey = generate_passkey()
                    student['status'] = 'approved'
                    student['passkey'] = passkey
                    approved_students.append(student)
                    # Send email with passkey
                    send_passkey_email(student['email'], passkey, student['name'])
                elif action == 'reject':
                    student['status'] = 'rejected'
                break
        return redirect(url_for('admin'))
    return render_template('admin.html', admissions=admissions)

# Exam access route
@app.route('/exam', methods=['GET', 'POST'])
def exam():
    if request.method == 'POST':
        passkey = request.form['passkey']
        for student in approved_students:
            if student.get('passkey') == passkey:
                return render_template('exam_access.html')  # Redirect to new page
        return render_template('exam.html', error="Invalid passkey")
    return render_template('exam.html', error=None)

# Exam access page (new route for successful passkey submission)
@app.route('/exam_access')
def exam_access():
    return render_template('exam_access.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)