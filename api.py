from flask import Flask, request, jsonify
from flask_cors import CORS
from ai_dev_assistant import askCodebase, load_knowledge_base
from dotenv import load_dotenv
import os
from session_manager import session_manager

DOCUMENTATION_COMMAND = "command: documentation, language: {language}"
UNIT_TEST_COMMAND = "command: unit-test, language: {language}"
CODE_REVIEW_COMMAND = "command: code-review, language: {language}"

load_dotenv()

app = Flask(__name__)
allowed_origins = [
    "https://ai-web-dev-assistant.vercel.app",
    "https://licenta-fe-stanescu.onrender.com"
]
CLIENT_ID = os.getenv("CLIENT_ID")
CORS(
    app, 
    resources={r"/*": {"origins": allowed_origins}},
    supports_credentials=True
)


@app.before_request
def check_client_id():
    client_id = request.headers.get("Client-Id")
    if client_id != CLIENT_ID and request.method != 'OPTIONS':
        return jsonify({"error": "Unauthorized"}), 401
    
@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Client-Id, Language, Session-Id"
    return response


@app.route('/documentation', methods=['GET'])
def documentation():
    session_id = request.headers.get("Session-Id")
    if not session_id:
        return jsonify({"error": "Session-Id header is required"}), 400
    responseLanguage = request.headers.get("language", "en")
    resp = askCodebase(DOCUMENTATION_COMMAND.format(language=responseLanguage), session_id)
    return jsonify({"answer": resp})

@app.route('/unit-test', methods=['GET'])
def unit_tests():
    session_id = request.headers.get("Session-Id")
    if not session_id:
        return jsonify({"error": "Session-Id header is required"}), 400
    responseLanguage = request.headers.get("language", "en")
    resp = askCodebase(UNIT_TEST_COMMAND.format(language=responseLanguage), session_id)
    return jsonify({"answer": resp}) 

@app.route('/code-review', methods=['GET'])
def code_review():
    session_id = request.headers.get("Session-Id")
    if not session_id:
        return jsonify({"error": "Session-Id header is required"}), 400
    responseLanguage = request.headers.get("language", "en")
    resp = askCodebase(CODE_REVIEW_COMMAND.format(language=responseLanguage), session_id)
    return jsonify({"answer": resp})


UPLOAD_FOLDER = 'knowledge_base'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload-directory', methods=['POST'])
def upload_directory():
    session_id = request.headers.get("Session-Id")
    if not session_id:
        return jsonify({"error": "Session-Id header is required"}), 400

    if 'files[]' not in request.files:
        return jsonify({"error": "No files part in the request"}), 400

    files = request.files.getlist('files[]')
    if not files:
        return jsonify({"error": "No files selected"}), 400

    session_manager.clear_session_files(session_id)

    session_upload_folder = os.path.join(UPLOAD_FOLDER, session_id)
    os.makedirs(session_upload_folder, exist_ok=True)

    saved_files = []
    try:
        for file in files:
            if file.filename: 
                file_path = os.path.join(session_upload_folder, file.filename)
                file.save(file_path)
                saved_files.append(file.filename)
        
        load_knowledge_base(session_id)
        return jsonify({
            "message": "Files uploaded successfully and knowledge base updated",
            "files": saved_files
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 4000))
    app.run(host="0.0.0.0", port=port)