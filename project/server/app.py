from flask import Flask, request, jsonify, send_file
import os
import shutil
import json
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
STORAGE_PATH = os.path.join(os.path.dirname(__file__), 'storage')
if not os.path.exists(STORAGE_PATH):
    os.makedirs(STORAGE_PATH)

# Authentication middleware (simple in-memory for demo)
USERS = {
    'admin': {'password': 'admin', 'name': 'Administrator'},
    'user': {'password': 'user', 'name': 'Regular User'}
}

def authenticate(username, password):
    if username in USERS and USERS[username]['password'] == password:
        return USERS[username]
    return None

# File system operations
@app.route('/api/auth', methods=['POST'])
def auth():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = authenticate(username, password)
    if user:
        return jsonify({
            'success': True,
            'user': {
                'username': username,
                'name': user['name']
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid credentials'
        }), 401

@app.route('/api/files', methods=['GET'])
def list_files():
    path = request.args.get('path', '')
    full_path = os.path.join(STORAGE_PATH, path)
    
    # Ensure the path exists and is within our storage area
    if not os.path.exists(full_path) or not os.path.normpath(full_path).startswith(STORAGE_PATH):
        return jsonify([])
    
    items = []
    for item in os.listdir(full_path):
        item_path = os.path.join(full_path, item)
        is_dir = os.path.isdir(item_path)
        
        # Get file stats
        stats = os.stat(item_path)
        
        # Format size for display
        if is_dir:
            size = '--'
        elif stats.st_size < 1024:
            size = f"{stats.st_size} B"
        elif stats.st_size < 1024 * 1024:
            size = f"{stats.st_size / 1024:.1f} KB"
        else:
            size = f"{stats.st_size / (1024 * 1024):.1f} MB"
        
        items.append({
            'name': item,
            'type': 'folder' if is_dir else 'file',
            'size': size,
            'modified': stats.st_mtime
        })
    
    return jsonify(items)

@app.route('/api/folders', methods=['POST'])
def create_folder():
    data = request.json
    path = data.get('path', '')
    name = data.get('name', '')
    
    if not name:
        return jsonify({
            'success': False,
            'message': 'Folder name is required'
        }), 400
    
    full_path = os.path.join(STORAGE_PATH, path, name)
    
    # Ensure the parent path exists and is within our storage area
    parent_path = os.path.join(STORAGE_PATH, path)
    if not os.path.exists(parent_path) or not os.path.normpath(parent_path).startswith(STORAGE_PATH):
        return jsonify({
            'success': False,
            'message': 'Invalid path'
        }), 400
    
    # Check if folder already exists
    if os.path.exists(full_path):
        return jsonify({
            'success': False,
            'message': 'Folder already exists'
        }), 400
    
    try:
        os.makedirs(full_path)
        return jsonify({
            'success': True,
            'message': 'Folder created successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/files', methods=['POST'])
def create_file():
    data = request.json
    path = data.get('path', '')
    name = data.get('name', '')
    content = data.get('content', '')
    
    if not name:
        return jsonify({
            'success': False,
            'message': 'File name is required'
        }), 400
    
    full_path = os.path.join(STORAGE_PATH, path, name)
    
    # Ensure the parent path exists and is within our storage area
    parent_path = os.path.join(STORAGE_PATH, path)
    if not os.path.exists(parent_path) or not os.path.normpath(parent_path).startswith(STORAGE_PATH):
        return jsonify({
            'success': False,
            'message': 'Invalid path'
        }), 400
    
    # Check if file already exists
    if os.path.exists(full_path):
        return jsonify({
            'success': False,
            'message': 'File already exists'
        }), 400
    
    try:
        with open(full_path, 'w') as f:
            f.write(content)
        return jsonify({
            'success': True,
            'message': 'File created successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/files/content', methods=['GET'])
def get_file_content():
    path = request.args.get('path', '')
    full_path = os.path.join(STORAGE_PATH, path)
    
    # Ensure the path exists and is within our storage area
    if not os.path.exists(full_path) or not os.path.normpath(full_path).startswith(STORAGE_PATH):
        return jsonify({
            'success': False,
            'message': 'File not found'
        }), 404
    
    # Ensure it's a file
    if not os.path.isfile(full_path):
        return jsonify({
            'success': False,
            'message': 'Not a file'
        }), 400
    
    try:
        with open(full_path, 'r') as f:
            content = f.read()
        return jsonify({
            'success': True,
            'content': content
        })
    except UnicodeDecodeError:
        # Binary file
        return jsonify({
            'success': False,
            'message': 'Binary file cannot be displayed'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/files/content', methods=['PUT'])
def update_file_content():
    data = request.json
    path = data.get('path', '')
    content = data.get('content', '')
    
    full_path = os.path.join(STORAGE_PATH, path)
    
    # Ensure the path exists and is within our storage area
    if not os.path.exists(full_path) or not os.path.normpath(full_path).startswith(STORAGE_PATH):
        return jsonify({
            'success': False,
            'message': 'File not found'
        }), 404
    
    # Ensure it's a file
    if not os.path.isfile(full_path):
        return jsonify({
            'success': False,
            'message': 'Not a file'
        }), 400
    
    try:
        with open(full_path, 'w') as f:
            f.write(content)
        return jsonify({
            'success': True,
            'message': 'File updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/move', methods=['POST'])
def move_item():
    data = request.json
    source = data.get('source', '')
    destination = data.get('destination', '')
    
    source_path = os.path.join(STORAGE_PATH, source)
    dest_path = os.path.join(STORAGE_PATH, destination)
    
    # Ensure both paths exist and are within our storage area
    if not os.path.exists(source_path) or not os.path.normpath(source_path).startswith(STORAGE_PATH):
        return jsonify({
            'success': False,
            'message': 'Source not found'
        }), 404
    
    # Ensure destination parent exists
    dest_parent = os.path.dirname(dest_path)
    if not os.path.exists(dest_parent) or not os.path.normpath(dest_parent).startswith(STORAGE_PATH):
        return jsonify({
            'success': False,
            'message': 'Destination parent not found'
        }), 400
    
    # Check if destination already exists
    if os.path.exists(dest_path):
        return jsonify({
            'success': False,
            'message': 'Destination already exists'
        }), 400
    
    try:
        shutil.move(source_path, dest_path)
        return jsonify({
            'success': True,
            'message': 'Item moved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/copy', methods=['POST'])
def copy_item():
    data = request.json
    source = data.get('source', '')
    destination = data.get('destination', '')
    
    source_path = os.path.join(STORAGE_PATH, source)
    dest_path = os.path.join(STORAGE_PATH, destination)
    
    # Ensure both paths exist and are within our storage area
    if not os.path.exists(source_path) or not os.path.normpath(source_path).startswith(STORAGE_PATH):
        return jsonify({
            'success': False,
            'message': 'Source not found'
        }), 404
    
    # Ensure destination parent exists
    dest_parent = os.path.dirname(dest_path)
    if not os.path.exists(dest_parent) or not os.path.normpath(dest_parent).startswith(STORAGE_PATH):
        return jsonify({
            'success': False,
            'message': 'Destination parent not found'
        }), 400
    
    # Check if destination already exists
    if os.path.exists(dest_path):
        return jsonify({
            'success': False,
            'message': 'Destination already exists'
        }), 400
    
    try:
        if os.path.isdir(source_path):
            shutil.copytree(source_path, dest_path)
        else:
            shutil.copy2(source_path, dest_path)
        return jsonify({
            'success': True,
            'message': 'Item copied successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/rename', methods=['POST'])
def rename_item():
    data = request.json
    path = data.get('path', '')
    new_name = data.get('newName', '')
    
    if not new_name:
        return jsonify({
            'success': False,
            'message': 'New name is required'
        }), 400
    
    full_path = os.path.join(STORAGE_PATH, path)
    dir_name = os.path.dirname(full_path)
    new_path = os.path.join(dir_name, new_name)
    
    # Ensure the path exists and is within our storage area
    if not os.path.exists(full_path) or not os.path.normpath(full_path).startswith(STORAGE_PATH):
        return jsonify({
            'success': False,
            'message': 'Item not found'
        }), 404
    
    # Check if destination already exists
    if os.path.exists(new_path):
        return jsonify({
            'success': False,
            'message': 'An item with this name already exists'
        }), 400
    
    try:
        os.rename(full_path, new_path)
        return jsonify({
            'success': True,
            'message': 'Item renamed successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/delete', methods=['DELETE'])
def delete_item():
    data = request.json
    path = data.get('path', '')
    
    full_path = os.path.join(STORAGE_PATH, path)
    
    # Ensure the path exists and is within our storage area
    if not os.path.exists(full_path) or not os.path.normpath(full_path).startswith(STORAGE_PATH):
        return jsonify({
            'success': False,
            'message': 'Item not found'
        }), 404
    
    try:
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        return jsonify({
            'success': True,
            'message': 'Item deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_files():
    path = request.form.get('path', '')
    uploaded_files = request.files.getlist('files')
    
    if not uploaded_files:
        return jsonify({
            'success': False,
            'message': 'No files were uploaded'
        }), 400
    
    target_dir = os.path.join(STORAGE_PATH, path)
    
    # Ensure the path exists and is within our storage area
    if not os.path.exists(target_dir) or not os.path.normpath(target_dir).startswith(STORAGE_PATH):
        return jsonify({
            'success': False,
            'message': 'Invalid path'
        }), 400
    
    try:
        successful = []
        failed = []
        
        for file in uploaded_files:
            filename = secure_filename(file.filename)
            file_path = os.path.join(target_dir, filename)
            
            # Check if file already exists
            if os.path.exists(file_path):
                failed.append({
                    'name': filename,
                    'reason': 'File already exists'
                })
                continue
            
            file.save(file_path)
            successful.append(filename)
        
        return jsonify({
            'success': True,
            'message': f"{len(successful)} file(s) uploaded successfully",
            'successful': successful,
            'failed': failed
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/download', methods=['GET'])
def download_file():
    path = request.args.get('path', '')
    full_path = os.path.join(STORAGE_PATH, path)
    
    # Ensure the path exists and is within our storage area
    if not os.path.exists(full_path) or not os.path.normpath(full_path).startswith(STORAGE_PATH):
        return jsonify({
            'success': False,
            'message': 'File not found'
        }), 404
    
    # Ensure it's a file
    if not os.path.isfile(full_path):
        return jsonify({
            'success': False,
            'message': 'Not a file'
        }), 400
    
    try:
        return send_file(full_path, as_attachment=True)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Run the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)