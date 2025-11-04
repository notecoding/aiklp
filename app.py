from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from model.infer import run_inference
from utils.analysis import analyze_results
import os

app = Flask(__name__)

# ✅ React 개발 서버(포트 3000)와 통신 허용
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return jsonify({"message": "AI Organizer API is running"}), 200


# ✅ React → Flask로 이미지 업로드 및 분석 요청
@app.route('/analyze', methods=['POST'])
def analyze_image():
    # 1️⃣ 이미지 파일 확인
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    file = request.files['image']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # 2️⃣ YOLO 모델 추론 실행
    try:
        detections, result_img_path = run_inference(filepath, RESULT_FOLDER)
    except Exception as e:
        return jsonify({'error': f'Model inference failed: {str(e)}'}), 500

    # 3️⃣ 분석 결과 및 리포트 생성
    try:
        report = analyze_results(detections)
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

    # 4️⃣ 결과 반환 (React가 이 JSON을 받음)
    return jsonify({
        "status": "success",
        "detections": detections,
        "report": report,
        "result_image": f"/results/{os.path.basename(result_img_path)}"
    })


# ✅ 분석된 이미지 파일 제공 (React에서 표시할 때 사용)
@app.route('/results/<path:filename>')
def serve_result_image(filename):
    return send_from_directory(RESULT_FOLDER, filename)


if __name__ == "__main__":
    # host="0.0.0.0" 은 로컬 전체 허용 / debug=True는 개발 편의용
    app.run(debug=True, host="0.0.0.0", port=5000)
