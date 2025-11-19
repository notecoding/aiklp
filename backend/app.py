from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from model.infer import run_inference
from utils.analysis import analyze_results
from utils.heatmap import generate_heatmap
from db import init_db, save_analysis, get_history, get_statistics
import os

app = Flask(__name__)

# CORS 설정
CORS(
    app,
    resources={r"/*": {"origins": "http://localhost:3000"}},
    supports_credentials=True
)

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# 서버 시작 시 DB 초기화
init_db()

@app.route('/')
def home():
    return jsonify({"message": "AI Organizer API is running"}), 200

@app.route('/analyze', methods=['POST'])
def analyze_image():
    """
    🎯 메인 분석 엔드포인트
    
    기능:
    1. 이미지 업로드
    2. YOLO 추론
    3. 개선된 분석 (가중치 기반)
    4. 히트맵 생성
    5. DB 저장
    """
    
    # 1. 이미지 파일 확인
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    # 2. YOLO 추론
    try:
        detections, result_img_path = run_inference(filepath, RESULT_FOLDER)
    except Exception as e:
        return jsonify({'error': f'Model inference failed: {str(e)}'}), 500
    
    # 3. 개선된 분석 실행
    try:
        report = analyze_results(detections)
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
    
    # 4. 히트맵 생성
    heatmap_path = None
    if detections:
        try:
            heatmap_filename = 'heatmap_' + file.filename
            heatmap_full_path = os.path.join(RESULT_FOLDER, heatmap_filename)
            generate_heatmap(filepath, detections, heatmap_full_path)
            heatmap_path = f"/results/{heatmap_filename}"
            print(f"✅ 히트맵 생성 완료: {heatmap_filename}")
        except Exception as e:
            print(f"⚠️ 히트맵 생성 실패: {e}")
    
    # 5. DB 저장
    try:
        analysis_id = save_analysis(
            score=report['score'],
            detections=detections,
            report=report,
            image_name=file.filename
        )
        print(f"✅ DB 저장 완료 (ID: {analysis_id})")
    except Exception as e:
        print(f"⚠️ DB 저장 실패: {e}")
    
    # 6. 응답 반환
    response_data = {
        "status": "success",
        "detections": detections,
        "report": report,
        "result_image": f"/results/{os.path.basename(result_img_path)}"
    }
    
    if heatmap_path:
        response_data["heatmap_image"] = heatmap_path
    
    return jsonify(response_data)

@app.route('/history', methods=['GET'])
def get_analysis_history():
    """분석 기록 조회"""
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)
        
        history = get_history(limit)
        return jsonify({
            "status": "success",
            "count": len(history),
            "history": history
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/statistics', methods=['GET'])
def get_stats():
    """통계 조회"""
    try:
        stats = get_statistics()
        return jsonify({
            "status": "success",
            "statistics": stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results/<path:filename>')
def serve_result_image(filename):
    """결과 이미지 제공"""
    return send_from_directory(RESULT_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)