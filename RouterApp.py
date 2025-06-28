from flask import Flask, request, jsonify, session
from flask_cors import CORS
import requests
import os
from waitress import serve

app = Flask(__name__)
app.secret_key = "secret-key"
CORS(app)

SERVICE_MAP = {
    "0": {
        "name": "Teacher",
        "url": "http://192.168.1.113:5000/TeacherAnswer" 
    },
    "4": {
        "name": "Student",
        "url": "http://192.168.1.113:5001/StudentAnswer"
    }
}


@app.route("/SelectSubject", methods=["POST"])
def select_subject():
    subject_code = request.form.get("subject_code")
    subject_names = {
        "01": "คณิตศาสตร์",
        "02": "ภาษาอังกฤษ",
        "03": "วิทยาศาสตร์",
        "04": "สังคมศึกษา",
        "05": "สุขศึกษา"
    }

    if subject_code not in subject_names:
        return jsonify({"error": "กรุณาระบุ subject_code ระหว่าง 01 ถึง 05"}), 400

    # ✅ สร้างโฟลเดอร์สำหรับข้อสอบ
    exam_folder = os.path.join("exam_json", subject_code)
    os.makedirs(exam_folder, exist_ok=True)

    # ✅ สร้างโฟลเดอร์สำหรับคะแนน
    score_folder = os.path.join("scores_json", subject_code)
    os.makedirs(score_folder, exist_ok=True)

    session["subject_code"] = subject_code
    session["subject_name"] = subject_names[subject_code]

    return jsonify({
        "message": f"เลือกวิชา {subject_names[subject_code]} เรียบร้อย",
        "next_url": "/SelectUser"
    })


@app.route("/SelectUser", methods=["POST"])
def select_user():
    user_id = request.form.get("user_id")
    if not user_id or len(user_id) != 5:
        return jsonify({"error": "กรุณาระบุ user_id 5 หลัก"}), 400

    prefix = user_id[0]
    if prefix not in SERVICE_MAP:
        return jsonify({"error": "user_id ต้องขึ้นต้นด้วย 0 (ครู) หรือ 4 (นักเรียน) เท่านั้น"}), 400

    session["user_id"] = user_id  # เก็บ session ไว้เหมือนเดิม

    if prefix == "0":  # ครู
        return jsonify({
            "message": f"user_id ขึ้นต้นด้วย {prefix} → กรุณากรอกข้อมูลที่ TeacherAnswer API โดยตรง",
            "note": "ไม่ต้องใช้ /SubmitData สำหรับครู"
        })
    else:
        # นักเรียน ยังต้องใช้ SubmitData ต่อ
        return jsonify({
            "message": f"user_id ขึ้นต้นด้วย {prefix} → ไปยัง {SERVICE_MAP[prefix]['name']}",
            "next_url": "/SubmitData",
            "note": "ให้ส่ง exam_id และ image ที่ปลายทางนี้"
        })

@app.route("/SubmitData", methods=["POST"])
def submit_data():
    user_id = session.get("user_id")
    subject_code = session.get("subject_code")
    exam_id = request.form.get("exam_id")
    image = request.files.get("image")

    if not user_id or not subject_code:
        return jsonify({"error": "ต้องเลือก subject_code และ user_id ก่อน"}), 400
    if not exam_id or not image:
        return jsonify({"error": "ต้องระบุ exam_id และแนบไฟล์ image"}), 400

    prefix = user_id[0]
    if prefix not in SERVICE_MAP:
        return jsonify({"error": "user_id ต้องขึ้นต้นด้วย 0 หรือ 4 เท่านั้น"}), 400

    target_url = SERVICE_MAP[prefix]["url"]

    try:
        resp = requests.post(
            target_url,
            data={
                "user_id": user_id,
                "exam_id": exam_id,
                "student_id": user_id,  # เฉพาะนักเรียน
                "subject_code": subject_code
            },
            files={"image": (image.filename, image.stream, image.content_type)}
        )

        return (resp.content, resp.status_code, resp.headers.items())

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5003)