from flask import Flask, jsonify, request
import os
import json
from waitress import serve

app = Flask(__name__)

SCORES_FOLDER = "scores_json"

# ตัวอย่าง mapping student_id -> seat_no
SEAT_MAP = {
    "40001": 2,
    "40002": 3,
    "40003": 1,
    "40004": 5,
    "40005": 4,
}

# ✅ ฟังก์ชันอ่านคะแนนจากไฟล์
def load_scores(subject_code, exam_id):
    path = os.path.join(SCORES_FOLDER, subject_code, f"{exam_id}_scores.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# ✅ endpoint สำหรับดึงคะแนนทั้งหมดของข้อสอบในวิชานั้น
@app.route("/GetScores", methods=["POST"])
def get_scores():
    subject_code = request.form.get("subject_code")
    exam_id = request.form.get("exam_id")

    if not subject_code or not exam_id:
        return jsonify({"error": "กรุณาส่ง subject_code และ exam_id ใน form data"}), 400

    scores = load_scores(subject_code, exam_id)
    result = []

    for sid, score_detail in scores.items():
        seat_no = SEAT_MAP.get(sid, 9999)

        # 🔧 แก้ตรงนี้ให้รองรับทั้ง dict และ int
        if isinstance(score_detail, dict):
            score = score_detail.get("score", 0)
            total = score_detail.get("total", 0)
        else:
            score = score_detail
            total = 0  # หรือใส่ค่าที่เหมาะสม

        result.append({
            "student_id": sid,
            "score": score,
            "total": total,
            "seat_no": seat_no
        })

    sorted_scores = sorted(result, key=lambda x: x["seat_no"])
    return jsonify(sorted_scores)

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5004)