import shutil
import os
import tempfile
import datetime
import traceback
from flask import Flask, send_file, request, jsonify, send_from_directory

app = Flask(__name__)

# Main directory containing the folders
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Folder that contains the files
FOLDER_PATH = "Tokens_Files"
CODES_FILE = "codes.txt"  # File storing activation codes with phone numbers

# Ensure the folder exists
if not os.path.exists(FOLDER_PATH):
    os.makedirs(FOLDER_PATH)

# Function to retrieve the phone number linked to the activation code
def get_phone_number(activation_code):
    if not os.path.exists(CODES_FILE):
        return None  # No file contains the codes

    with open(CODES_FILE, "r") as f:
        codes = dict(line.strip().split(",") for line in f if "," in line)  # Assume each line contains "code,phone"
    
    return codes.get(activation_code)  # Return phone number if found

# Function to load codes from a text file
def load_codes():
    try:
        codes = {}
        with open(CODES_FILE, "r") as file:
            for line in file:
                parts = line.strip().split(",")  # Split code and phone number
                if len(parts) == 2:
                    codes[parts[0]] = parts[1]  # Store code as key and phone as value
        return codes
    except FileNotFoundError:
        return {}  # Return empty dict if file not found

# Function to save codes in a text file
def save_code(new_code, phone):
    with open(CODES_FILE, "a") as file:  # Use append instead of full rewrite
        file.write(new_code + "," + phone + "\n")

@app.route('/download_folder', methods=['GET'])
def download_folder():
    folder_name = request.args.get('folder')  # Get folder name from request
    
    if not folder_name:
        return jsonify({"error": "Folder name is required"}), 400
    
    folder_path = os.path.join(BASE_DIR, folder_name)

    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return jsonify({"error": "Folder not found"}), 404

    # Create a temporary zip file
    temp_dir = tempfile.mkdtemp()
    
    # Get current date and time in format YYYY-MM-DD_HH-MM-SS
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Create a new zip file name using date and time
    zip_filename = f"{folder_name}.zip"
    zip_path = os.path.join(temp_dir, zip_filename)

    shutil.make_archive(zip_path.replace('.zip', ''), 'zip', folder_path)  # Compress folder

    # Delete the original folder after compression
    shutil.rmtree(folder_path)

    return send_file(zip_path, as_attachment=True, download_name=zip_filename)

@app.route('/add_code', methods=['POST'])
def add_code():
    try:
        data = request.get_json()  # Receive JSON
        if not data:
            return jsonify({
                "status": "error",
                "message": "Invalid JSON format"
            }), 400

        new_code = data.get("code")
        phone = data.get("phone")

        if not new_code or not phone:
            return jsonify({
                "status": "error",
                "message": "Code and phone number are required"
            }), 400

        codes = load_codes()

        if new_code in codes:
            return jsonify({
                "status": "error",
                "message": "Code already exists"
            }), 400

        save_code(new_code, phone)  # Save code with phone in file

        return jsonify({
            "status": "success",
            "message": "Code added successfully"
        }), 200

    except Exception as e:
        print("❌ Server error:", e)
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": "Internal Server Error"
        }), 500

@app.route("/verify", methods=["POST"])
def verify_key():
    version = "1.0"

    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "❌ Invalid data received!"
            }), 400

        tool_version = data.get("tool_version")
        key = data.get("key")
        codes = load_codes()

        if key in codes:
            phone_number = codes[key]  # Get phone number linked to code
            
            if tool_version == version:
                return jsonify({
                    "status": "success",
                    "message": "✅ Activation successful!",
                    "phone": phone_number  # Send phone number in response
                }), 200
            else:
                return jsonify({
                    "status": "not",
                    "message": "❌ Activation failed!"
                }), 405
        else:
            return jsonify({
                "status": "error",
                "message": "❌ Invalid activation code!"
            }), 400

    except Exception as e:
        print("❌ Server error:", e)
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": "Internal Server Error"
        }), 500

@app.route('/store_token', methods=['POST'])
def store_token():
    data = request.json
    activation_code = data.get("activation_code")
    token = data.get("token")

    if not activation_code or not token:
        return jsonify({"error": "Missing activation_code or token"}), 400

    phone_number = get_phone_number(activation_code)

    if not phone_number:
        return jsonify({"error": "Phone number not found for this activation code"}), 404

    file_path = os.path.join(FOLDER_PATH, f"{phone_number}.txt")

    if os.path.exists(file_path):
        with open(file_path, "a") as f:
            f.write(f"{token}\n")
        return jsonify({"message": "Token added to existing file"}), 200

    with open(file_path, "w") as f:
        f.write(f"{activation_code}\n{token}\n")

    return jsonify({"message": "New file created and token stored"}), 201

@app.route('/')
def keep():
    return "Server is alive!", 200

@app.route('/get-token')
def serve_page():
    return send_from_directory('.', 'get-token.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
