from flask import Flask, request, jsonify
import os
import json
from waitress import serve

app = Flask(__name__)

SCORES_FOLDER = "scores_json"
os.makedirs(SCORES_FOLDER, exist_ok=True)

def load_scores(subject_code, exam_id):
    subject_folder = os.path.join(SCORES_FOLDER, subject_code)
    os.makedirs(subject_folder, exist_ok=True)
    path = os.path.join(subject_folder, f"{exam_id}_scores.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_scores(subject_code, exam_id, scores_dict):
    subject_folder = os.path.join(SCORES_FOLDER, subject_code)
    os.makedirs(subject_folder, exist_ok=True)
    path = os.path.join(subject_folder, f"{exam_id}_scores.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(scores_dict, f, ensure_ascii=False, indent=2)

@app.route("/ReceiveScore", methods=["POST"])
def receive_score():
    data = request.get_json()
    required_fields = ["exam_id", "student_id", "subject_code", "score", "total", "accuracy"]
    if not data or any(field not in data for field in required_fields):
        return jsonify({"error": "ข้อมูลไม่ครบถ้วน"}), 400

    exam_id = data["exam_id"]
    student_id = data["student_id"]
    subject_code = data["subject_code"]
    score = data["score"]
    total = data["total"]
    accuracy = data["accuracy"]

    scores = load_scores(subject_code, exam_id)
    scores[student_id] = {
        "score": score,
        "total": total,
        "accuracy": accuracy
    }
    save_scores(subject_code, exam_id, scores)

    return jsonify({"message": f"รับคะแนนของนักเรียน {student_id} เรียบร้อยแล้ว"}), 200

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5005)