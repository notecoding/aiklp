from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from model.infer import run_inference
from utils.analysis import analyze_results
import os

app = Flask(__name__)

# ✅ 수정된 CORS 설정 (React와 인증 포함 통신 허용)
CORS(
    app,
    resources={r"/*": {"origins": "http://localhost:3000"}},
    supports_credentials=True   # 🔥 이 한 줄이 핵심
)

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return jsonify({"message": "AI Organizer API is running"}), 200

@app.route('/analyze', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    file = request.files['image']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        detections, result_img_path = run_inference(filepath, RESULT_FOLDER)
    except Exception as e:
        return jsonify({'error': f'Model inference failed: {str(e)}'}), 500

    try:
        report = analyze_results(detections)
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

    return jsonify({
        "status": "success",
        "detections": detections,
        "report": report,
        "result_image": f"/results/{os.path.basename(result_img_path)}"
    })

@app.route('/results/<path:filename>')
def serve_result_image(filename):
    return send_from_directory(RESULT_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
