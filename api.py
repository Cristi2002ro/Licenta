from flask import Flask, request, jsonify, send_file
from flask_cors import CORS  # Import CORS
from gpt4o import askCodebase, load_knowledge_base
import os
import prompts

app = Flask(__name__)
CORS(
    app, 
    resources={r"/*": {"origins": "https://v0-dev-assistent.vercel.app"}},
    supports_credentials=True
)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "https://v0-dev-assistent.vercel.app"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Ai-Model, Access-Control-Allow-Origin"
    return response

@app.route('/ask', methods=['GET'])
def ask_question():
    model = request.headers.get("Ai-Model")
    question = request.json.get("question")
    if question is None:
        return jsonify({"error":"Field question is missing"}),400
    return jsonify({"answer": askCodebase(question, model)})

#todo de adaugat? parametru optional de additional prompt pt completari ulterioare si adaugiri la prompt in caz ca raspunsul initial nu e bun
@app.route('/documentation', methods=['GET'])
def documentation():
    model = request.headers.get("Ai-Model")
    resp = askCodebase(prompts.documentation_prompt, model)
    
    return jsonify({"answer": resp})

@app.route('/unit-test', methods=['GET'])
def unit_tests():
    model = request.headers.get("Ai-Model")
    resp = askCodebase(prompts.unit_tests_prompt, model)
    return jsonify({"answer": resp}) 

@app.route('/code-review', methods=['GET'])
def code_review():
    model = request.headers.get("Ai-Model")
    resp = askCodebase(prompts.code_review, model)
    return jsonify({"answer": resp})


UPLOAD_FOLDER = 'knowledge_base'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload-directory', methods=['POST'])
def upload_directory():
    if 'files[]' not in request.files:
        return jsonify({"error": "No files part in the request"}), 400

    files = request.files.getlist('files[]')
    
    if not files:
        return jsonify({"error": "No files selected"}), 400

    saved_files = []
    try:
        for file in files:
            if file.filename: 
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                saved_files.append(file.filename)
        
        load_knowledge_base()
        return jsonify({
            "message": "Files uploaded successfully",
            "files": saved_files
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)