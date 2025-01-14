from flask import Flask, request, jsonify
from app import askCodebase

app = Flask(__name__)

@app.route('/ask', methods=['GET'])
def ask_question():
    #question = request.json.get("question")
    return jsonify({"answer": askCodebase()})

if __name__ == "__main__":
    app.run(debug=True)