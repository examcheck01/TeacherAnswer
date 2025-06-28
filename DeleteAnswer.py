from flask import Flask, request, jsonify
import os
from waitress import serve  

app = Flask(__name__)

OUTPUT_FOLDER = "exam_json"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/DeleteAnswer", methods=["POST"])
def delete_answer_key():
    exam_id = request.form.get("exam_id")
    if not exam_id:
        return jsonify({"error": "No exam_id provided"}), 400

    filename = f"{exam_id}_answers.json"
    file_path = os.path.join(OUTPUT_FOLDER, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": f"No answer key file found for exam_id {exam_id}."}), 404

    try:
        os.remove(file_path)
        return jsonify({"message": f"Deleted answer key file for exam_id {exam_id}."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5002)  