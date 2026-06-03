"""
CyberGuard Website - Contact Form Backend
Vercel-compatible version with in-memory storage
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# In-memory storage (Vercel compatible)
contacts_db = []
contact_id_counter = 1

# Admin credentials
ADMIN_KEY = "CyberGuard2026!"

# ============ ROUTES ============

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/admin_login.html')
def serve_admin_login():
    return send_from_directory('.', 'admin_login.html')

@app.route('/admin_dashboard.html')
def serve_admin_dashboard():
    return send_from_directory('.', 'admin_dashboard.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(path):
        return send_from_directory('.', path)
    return "File not found", 404

# ============ CONTACT FORM API ============

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    global contact_id_counter
    try:
        data = request.get_json()
        
        required = ['name', 'phone', 'email', 'reason']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        contact = {
            'id': contact_id_counter,
            'name': data['name'].strip(),
            'phone': data['phone'].strip(),
            'email': data['email'].strip(),
            'reason': data['reason'],
            'message': data.get('message', ''),
            'ip_address': request.headers.get('X-Forwarded-For', request.remote_addr),
            'timestamp': datetime.now().isoformat(),
            'status': 'new'
        }
        
        contacts_db.append(contact)
        contact_id_counter += 1
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully!',
            'id': contact['id']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ ADMIN API ============

def check_auth():
    return request.headers.get('X-Admin-Key') == ADMIN_KEY

@app.route('/admin/contacts', methods=['GET'])
def get_all_contacts():
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'contacts': contacts_db[::-1]}), 200

@app.route('/admin/contacts/<int:contact_id>/read', methods=['PUT'])
def mark_read(contact_id):
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    
    for contact in contacts_db:
        if contact['id'] == contact_id:
            contact['status'] = 'read'
            return jsonify({'success': True}), 200
    return jsonify({'error': 'Not found'}), 404

@app.route('/admin/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    
    global contacts_db
    contacts_db = [c for c in contacts_db if c['id'] != contact_id]
    return jsonify({'success': True}), 200

@app.route('/admin/stats', methods=['GET'])
def get_stats():
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    
    total = len(contacts_db)
    new = len([c for c in contacts_db if c['status'] == 'new'])
    theft = len([c for c in contacts_db if c['reason'] == 'theft'])
    read = total - new
    
    return jsonify({'total': total, 'new': new, 'read': read, 'theft': theft}), 200

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        'status': 'online',
        'total_contacts': len(contacts_db),
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
