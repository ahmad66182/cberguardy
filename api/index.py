from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime

# MongoDB use karo (SQLite ki jagah)
import pymongo

app = Flask(__name__)
CORS(app)

# MongoDB connection (Vercel compatible)
MONGO_URI = os.environ.get('MONGODB_URI', 'your_mongodb_uri_here')
client = pymongo.MongoClient(MONGO_URI)
db = client['cyberguard']
contacts_collection = db['contacts']

# Admin auth
ADMIN_KEY = "CyberGuard2026!"

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'project': 'CyberGuard Website',
        'status': 'active',
        'message': 'Contact form backend is running'
    })

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    try:
        data = request.get_json()
        
        # Validation
        required = ['name', 'phone', 'email', 'reason']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'{field} required'}), 400
        
        contact = {
            'name': data['name'].strip(),
            'phone': data['phone'].strip(),
            'email': data['email'].strip(),
            'reason': data['reason'],
            'message': data.get('message', ''),
            'ip_address': request.headers.get('X-Forwarded-For', request.remote_addr),
            'timestamp': datetime.now().isoformat(),
            'status': 'new'
        }
        
        result = contacts_collection.insert_one(contact)
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully!',
            'id': str(result.inserted_id)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/contacts', methods=['GET'])
def get_contacts():
    auth = request.headers.get('X-Admin-Key')
    if auth != ADMIN_KEY:
        return jsonify({'error': 'Unauthorized'}), 401
    
    contacts = list(contacts_collection.find({}, {'_id': 0}).sort('timestamp', -1))
    return jsonify({'contacts': contacts}), 200

@app.route('/api/status', methods=['GET'])
def get_status():
    total = contacts_collection.count_documents({})
    new = contacts_collection.count_documents({'status': 'new'})
    
    return jsonify({
        'status': 'online',
        'total_contacts': total,
        'new_contacts': new,
        'timestamp': datetime.now().isoformat()
    }), 200

# For local development
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
