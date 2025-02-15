from flask import Flask, request, jsonify, send_file
from gpt4o import askCodebase
from utils import save_response_to_file
import os
import prompts

app = Flask(__name__)

@app.route('/ask', methods=['GET'])
def ask_question():
    question = request.json.get("question")
    if question is None:
        return jsonify({"error":"Field question is missing"}),400
    return jsonify({"answer": askCodebase(question)})

#de adaugat? parametru optional de additional prompt pt completari ulterioare si adaugiri la prompt in caz ca raspunsul initial nu e bun
@app.route('/documentation', methods=['GET'])
def documentation():
    # Obține răspunsul din funcția askCodebase
    resp = askCodebase(prompts.documentation_prompt)
    
    # Salvează fișierul markdown
    file_name = "documentation.md"
    save_response_to_file(resp, file_name)
    
    # Returnează fișierul generat
    return send_file(file_name, as_attachment=True)

@app.route('/unit-test', methods=['GET'])
def unit_tests():
     # Obține răspunsul din funcția askCodebase
    resp = askCodebase(prompts.unit_tests_prompt)
    
    # Salvează fișierul markdown
    file_name = "tests.py"
    save_response_to_file(resp, file_name)
    
    # Returnează fișierul generat
    return send_file(file_name, as_attachment=True)

@app.route('/code-review', methods=['GET'])
def code_review():
     # Obține răspunsul din funcția askCodebase
    resp = askCodebase(prompts.code_review)
    return resp


# Define folderul unde vor fi salvate fisierele
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
        
        return jsonify({
            "message": "Files uploaded successfully",
            "files": saved_files
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)