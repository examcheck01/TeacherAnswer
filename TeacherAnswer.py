import tempfile
import pandas as pd
from flask import Flask, request, jsonify
from roboflow import Roboflow
import os
import json
from waitress import serve

app = Flask(__name__)

# หาตำแหน่งโฟลเดอร์ที่ไฟล์นี้อยู่ (TeacherAnswer.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# กำหนดโฟลเดอร์เก็บ JSON ให้สัมพันธ์กับ BASE_DIR
OUTPUT_FOLDER = os.path.join(BASE_DIR, "exam_json")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

print("Current directory:", os.getcwd())
print("Output folder:", OUTPUT_FOLDER)

@app.route("/TeacherAnswer", methods=["POST"])
def Teacher_answer_key():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image = request.files["image"]

    # สร้างไฟล์ภาพชั่วคราว
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        temp_filename = tmp.name
        image.save(temp_filename)

    try:
        # วิเคราะห์ด้วย Roboflow
        rf = Roboflow(api_key="6vQ5WhBrn1ChGkwMqLJN")
        project = rf.workspace("omgggg").project("omg-peper")
        model = project.version(4).model

        result = model.predict(temp_filename, confidence=70, overlap=30).json()
        predictions = result.get("predictions", [])

        if predictions:
            df = pd.DataFrame(predictions)
            df_sorted = df.sort_values(by="y").reset_index(drop=True)
            df_sorted.insert(0, "index", df_sorted.index + 1)
            output = df_sorted[["index", "class", "confidence", "x", "y", "width", "height"]].to_dict(orient="records")

            # สร้าง exam_id แบบเรียงลำดับ
            existing_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.startswith("exam_") and f.endswith("_answers.json")]
            numbers = []
            for f in existing_files:
                try:
                    number = int(f.split("_")[1])
                    numbers.append(number)
                except (IndexError, ValueError):
                    continue

            next_number = max(numbers) + 1 if numbers else 1
            exam_id = f"exam_{next_number:03}"
            json_filename = os.path.join(OUTPUT_FOLDER, f"{exam_id}_answers.json")

            # บันทึกผลลัพธ์
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump({"exam_id": exam_id, "sorted_predictions": output}, f, ensure_ascii=False, indent=2)

            return jsonify({
                "exam_id": exam_id,
                "sorted_predictions": output
            })

        else:
            return jsonify({"sorted_predictions": [], "message": "ไม่พบการตรวจจับ"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)