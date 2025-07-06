#!/usr/bin/env python3
"""
Flask-based Ticket Management System
Converted from Streamlit application for Render deployment
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import pandas as pd
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date, timedelta
from io import BytesIO
import os
from functools import wraps

# Import auth system
from auth.models import db, User
from auth.routes import auth, login_required, admin_required
from auth.utils import hash_password, verify_password

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ticket_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
db.init_app(app)

# Register auth blueprint
app.register_blueprint(auth, url_prefix='/auth')

# Database Models (Ticket-related only - User model is in auth.models)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50), nullable=False)
    court_date = db.Column(db.Date)
    citation_date = db.Column(db.Date)
    contact_date = db.Column(db.Date)
    ticket_type = db.Column(db.String(50))
    county = db.Column(db.String(50))
    court = db.Column(db.String(100))
    notes = db.Column(db.Text)
    source = db.Column(db.String(100))
    other = db.Column(db.String(100))
    ticket_image = db.Column(db.LargeBinary)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RawUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text)  # JSON string of uploaded data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Authentication is now handled by the auth blueprint

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
@login_required
def dashboard():
    ticket_count = Ticket.query.count()
    return render_template('dashboard.html', ticket_count=ticket_count, current_date=datetime.now())

@app.route('/add_ticket', methods=['GET', 'POST'])
@login_required
def add_ticket():
    if request.method == 'POST':
        # Handle ticket creation
        ticket = Ticket(
            first_name=request.form['first_name'],
            middle_name=request.form['middle_name'],
            last_name=request.form['last_name'],
            court_date=datetime.strptime(request.form['court_date'], '%Y-%m-%d').date() if request.form['court_date'] else None,
            citation_date=datetime.strptime(request.form['citation_date'], '%Y-%m-%d').date() if request.form['citation_date'] else None,
            contact_date=datetime.strptime(request.form['contact_date'], '%Y-%m-%d').date() if request.form['contact_date'] else None,
            ticket_type=request.form['ticket_type'],
            county=request.form['county'],
            court=request.form['court'],
            notes=request.form['notes'],
            source=request.form['source'],
            other=request.form['other']
        )
        
        # Handle file upload
        if 'ticket_image' in request.files:
            file = request.files['ticket_image']
            if file and file.filename:
                ticket.ticket_image = file.read()
        
        db.session.add(ticket)
        db.session.commit()
        
        flash('Ticket added successfully!', 'success')
        return redirect(url_for('view_tickets'))
    
    return render_template('add_ticket.html')

@app.route('/upload_tickets', methods=['GET', 'POST'])
@login_required
def upload_tickets():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and file.filename.endswith('.xlsx'):
            try:
                # Read Excel file
                df = pd.read_excel(file, header=0)
                if df.columns.tolist()[0].startswith("Unnamed"):
                    df.columns = [f"Column {i+1}" for i in range(len(df.columns))]
                
                # Save to database with better JSON structure
                raw_upload = RawUpload(data=df.to_json(orient='records'))
                db.session.add(raw_upload)
                db.session.commit()
                
                flash('File imported and saved successfully!', 'success')
                return redirect(url_for('view_tickets'))
            except Exception as e:
                flash(f'Error processing file: {e}', 'error')
        else:
            flash('Please upload an Excel file (.xlsx)', 'error')
    
    return render_template('upload_tickets.html')

@app.route('/view_tickets')
@login_required
def view_tickets():
    table_choice = request.args.get('table', 'tickets')
    
    if table_choice == 'tickets':
        tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
        raw_uploads = []
        return render_template('view_tickets.html', tickets=tickets, raw_uploads=raw_uploads, table_choice=table_choice)
    else:
        tickets = []
        raw_uploads = RawUpload.query.order_by(RawUpload.created_at.desc()).all()
        return render_template('view_tickets.html', tickets=tickets, raw_uploads=raw_uploads, table_choice=table_choice)

@app.route('/delete_ticket/<int:ticket_id>', methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    flash('Ticket deleted successfully!', 'success')
    return redirect(url_for('view_tickets'))

@app.route('/export_tickets')
@login_required
def export_tickets():
    table_choice = request.args.get('table', 'tickets')
    
    if table_choice == 'tickets':
        tickets = Ticket.query.all()
        
        # Convert to DataFrame
        data = []
        for ticket in tickets:
            data.append({
                'ID': ticket.id,
                'First Name': ticket.first_name,
                'Middle Name': ticket.middle_name,
                'Last Name': ticket.last_name,
                'Court Date': ticket.court_date,
                'Citation Date': ticket.citation_date,
                'Contact Date': ticket.contact_date,
                'Ticket Type': ticket.ticket_type,
                'County': ticket.county,
                'Court': ticket.court,
                'Notes': ticket.notes,
                'Source': ticket.source,
                'Other': ticket.other,
                'Created At': ticket.created_at
            })
        
        df = pd.DataFrame(data)
        filename = f'tickets_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    else:
        raw_uploads = RawUpload.query.all()
        
        # Convert to DataFrame
        data = []
        for upload in raw_uploads:
            upload_data = pd.read_json(upload.data, orient='records')
            data.append(upload_data)
        
        if data:
            df = pd.concat(data, ignore_index=True)
        else:
            df = pd.DataFrame()
        
        filename = f'raw_uploads_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@app.route('/debug_upload/<int:upload_id>')
@login_required
def debug_upload(upload_id):
    upload = RawUpload.query.get_or_404(upload_id)
    import json
    try:
        data = json.loads(upload.data)
        return jsonify({
            'upload_id': upload.id,
            'data_type': type(data).__name__,
            'data_length': len(data) if isinstance(data, (list, dict)) else 'N/A',
            'data_preview': data[:2] if isinstance(data, list) else str(data)[:200]
        })
    except Exception as e:
        return jsonify({'error': str(e), 'raw_data': upload.data[:200]})

@app.route('/send_notification', methods=['GET', 'POST'])
@login_required
def send_notification():
    if request.method == 'POST':
        smtp_server = request.form['smtp_server']
        smtp_port = int(request.form['smtp_port'])
        smtp_username = request.form['smtp_username']
        smtp_password = request.form['smtp_password']
        recipient = request.form['recipient']
        subject = request.form['subject']
        message = request.form['message']
        
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            
            flash('Email sent successfully!', 'success')
        except Exception as e:
            flash(f'Failed to send email: {e}', 'error')
        
        return redirect(url_for('send_notification'))
    
    return render_template('send_notification.html')

# Jinja2 filters
@app.template_filter('from_json')
def from_json_filter(data):
    import json
    try:
        result = json.loads(data)
        # Ensure we return a list for records format
        if isinstance(result, dict):
            return []
        return result
    except:
        return []

# Initialize database and create default admin user
def init_db():
    with app.app_context():
        db.create_all()
        
        # Create default admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                password_hash=hash_password('admin123'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: admin/admin123")
        else:
            print("Admin user already exists")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 9000))) 