"""
CyberGuard Website - Contact Form Backend
Separate from Evidence Server - No connection to tracker data
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import hashlib
import secrets

# Fix: Use absolute path for database
import os
DATABASE = os.path.join(os.path.dirname(__file__), 'contacts.db')

# Initialize database function
def init_db():
    """Initialize database if it doesn't exist"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL,
                reason TEXT NOT NULL,
                message TEXT,
                ip_address TEXT,
                user_agent TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'new'
            )
        ''')
        conn.commit()
        conn.close()
        print(f"✅ Database initialized at: {DATABASE}")
        return True
    except Exception as e:
        print(f"❌ Database init error: {e}")
        return False

# Initialize database immediately
init_db()

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Admin credentials
ADMIN_KEY = "CyberGuard2026!"
ADMIN_USERNAME = "cyberguard_admin"
ADMIN_PASSWORD = "Secure@2026!"

# Email settings (optional)
EMAIL_ENABLED = False
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            reason TEXT NOT NULL,
            message TEXT,
            ip_address TEXT,
            user_agent TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'new'
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database initialized")

# Send email notification (optional)
def send_email_notification(contact_data):
    if not EMAIL_ENABLED:
        return
    
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = SMTP_EMAIL
        msg['Subject'] = f"New Contact: {contact_data['reason']}"
        
        body = f"""
        New Contact Form Submission
        
        Name: {contact_data['name']}
        Phone: {contact_data['phone']}
        Email: {contact_data['email']}
        Reason: {contact_data['reason']}
        Message: {contact_data['message']}
        IP: {contact_data['ip']}
        Time: {contact_data['timestamp']}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Email error: {e}")

# ============ MAIN ROUTES ============

@app.route('/')
def serve_index():
    """Serve the main website"""
    return send_from_directory('.', 'index.html')

@app.route('/admin_login.html')
def serve_admin_login():
    """Serve admin login page"""
    return send_from_directory('.', 'admin_login.html')

@app.route('/admin_dashboard.html')
def serve_admin_dashboard():
    """Serve admin dashboard"""
    return send_from_directory('.', 'admin_dashboard.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    if os.path.exists(path):
        return send_from_directory('.', path)
    return "File not found", 404

# ============ CONTACT FORM API ============

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    """Handle contact form submission"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['name', 'phone', 'email', 'reason']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email
        email = data['email'].strip()
        if '@' not in email:
            return jsonify({'error': 'Invalid email address'}), 400
        
        # Validate phone
        phone = data['phone'].strip()
        if len(phone) < 8:
            return jsonify({'error': 'Invalid phone number'}), 400
        
        # Get client info
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Prepare contact data
        contact = {
            'name': data['name'].strip(),
            'phone': phone,
            'email': email,
            'reason': data['reason'],
            'message': data.get('message', '').strip(),
            'ip': ip_address,
            'user_agent': user_agent,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save to database
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO contacts (name, phone, email, reason, message, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (contact['name'], contact['phone'], contact['email'], 
              contact['reason'], contact['message'], contact['ip'], contact['user_agent']))
        conn.commit()
        contact_id = c.lastrowid
        conn.close()
        
        # Send email notification (optional)
        send_email_notification(contact)
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully!',
            'id': contact_id
        }), 200
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ============ ADMIN API ENDPOINTS ============

def check_admin_auth():
    """Check admin authentication"""
    admin_key = request.headers.get('X-Admin-Key')
    return admin_key == ADMIN_KEY

@app.route('/admin/contacts', methods=['GET'])
def get_all_contacts():
    """Get all contacts for admin dashboard"""
    if not check_admin_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM contacts ORDER BY timestamp DESC")
        contacts = [dict(row) for row in c.fetchall()]
        conn.close()
        
        return jsonify({'contacts': contacts}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get single contact by ID"""
    if not check_admin_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        contact = c.fetchone()
        conn.close()
        
        if contact:
            return jsonify(dict(contact)), 200
        else:
            return jsonify({'error': 'Contact not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/contacts/<int:contact_id>/read', methods=['PUT'])
def mark_contact_read(contact_id):
    """Mark contact as read"""
    if not check_admin_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("UPDATE contacts SET status = 'read' WHERE id = ?", (contact_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Marked as read'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """Delete contact message"""
    if not check_admin_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        conn.commit()
        affected = c.rowcount
        conn.close()
        
        if affected > 0:
            return jsonify({'success': True, 'message': 'Deleted successfully'}), 200
        else:
            return jsonify({'error': 'Contact not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/stats', methods=['GET'])
def get_admin_stats():
    """Get statistics for admin dashboard"""
    if not check_admin_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM contacts")
        total = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM contacts WHERE status = 'new'")
        new = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM contacts WHERE reason = 'theft'")
        theft = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM contacts WHERE status = 'read'")
        read = c.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'total': total,
            'new': new,
            'read': read,
            'theft': theft
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ STATUS ENDPOINT ============

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get website status (no evidence data)"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Get counts
        c.execute("SELECT COUNT(*) FROM contacts")
        total_contacts = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM contacts WHERE status = 'new'")
        new_contacts = c.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'status': 'online',
            'total_contacts': total_contacts,
            'new_contacts': new_contacts,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============ MAIN ============

if __name__ == '__main__':
    init_db()
    print("="*50)
    print("🚀 CyberGuard Website Backend")
    print("📡 Running on: http://localhost:5001")
    print("="*50)
    print("📧 Contact form endpoint: POST /api/contact")
    print("🔐 Admin endpoints:")
    print("   - GET /admin/contacts")
    print("   - GET /admin/contacts/<id>")
    print("   - PUT /admin/contacts/<id>/read")
    print("   - DELETE /admin/contacts/<id>")
    print("   - GET /admin/stats")
    print("="*50)
    print(f"👤 Admin Username: {ADMIN_USERNAME}")
    print(f"🔑 Admin Password: {ADMIN_PASSWORD}")
    print("="*50)
    app.run(host='0.0.0.0', port=5001, debug=False)