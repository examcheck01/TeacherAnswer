import tempfile
import pandas as pd
from flask import Flask, request, jsonify
from roboflow import Roboflow
import os
import json
from waitress import serve

app = Flask(__name__)

OUTPUT_FOLDER = "exam_json"

@app.route("/StudentAnswer", methods=["POST"])
def Student_Answer_key():
    print("request.files:", request.files)  # ดูไฟล์ที่ส่งมา
    print("request.form:", request.form)    # ดูข้อมูล form ที่ส่งมา

    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image = request.files["image"]
    
    exam_id = request.form.get("exam_id")
    if not exam_id:
        return jsonify({"error": "No exam_id provided"}), 400
    
    student_id = request.form.get("student_id")
    if not student_id:
        return jsonify({"error": "No student_id provided"}), 400


    # โหลดไฟล์ answer key ที่เซฟไว้ตอน TeacherAnswer
    answer_file = os.path.join(OUTPUT_FOLDER, f"{exam_id}_answers.json")
    if not os.path.exists(answer_file):
        return jsonify({"error": f"Answer key file for exam_id {exam_id} not found"}), 404

    with open(answer_file, "r", encoding="utf-8") as f:
        answer_data = json.load(f)
        correct_answers = answer_data.get("sorted_predictions", [])

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        temp_filename = tmp.name
        image.save(temp_filename)

    try:
        rf = Roboflow(api_key="6vQ5WhBrn1ChGkwMqLJN")
        project = rf.workspace("omgggg").project("omg-peper")
        model = project.version(4).model

        result = model.predict(temp_filename, confidence=70, overlap=30).json()
        student_predictions = result.get("predictions", [])

        # จัดเรียงเหมือนกับ answer key เพื่อให้เปรียบเทียบได้ง่าย
        if student_predictions:
            df_student = pd.DataFrame(student_predictions).sort_values(by="y").reset_index(drop=True)
            df_student.insert(0, "index", df_student.index + 1)

            # สมมติว่าตรวจสอบแค่ class ว่าตรงกันหรือไม่ (ปรับได้ตามต้องการ)
            score = 0
            for i, ans in enumerate(correct_answers):
                if i < len(df_student) and ans["class"] == df_student.at[i, "class"]:
                    score += 1

            total = len(correct_answers)
            accuracy = score / total if total > 0 else 0

            return jsonify({
                "exam_id": exam_id,
                "score": score,
                "total": total,
                "accuracy": accuracy,
                "student_id":student_id,
            })
        else:
            return jsonify({"message": "ไม่พบการตรวจจับในคำตอบนักเรียน"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5001)