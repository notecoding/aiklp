from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from model.infer import run_inference
from utils.analysis import analyze_results
from utils.heatmap import generate_heatmap
from db import init_db, save_analysis, get_history, get_statistics
import os
from dotenv import load_dotenv
from openai import OpenAI


# ============================================
# 🔥 환경 변수 로드 및 OpenAI 클라이언트 생성
# ============================================
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️ WARNING: OPENAI_API_KEY 환경변수가 설정되지 않았습니다!")


# ============================================
# Flask 초기 설정
# ============================================
app = Flask(__name__)

CORS(
    app,
    resources={r"/*": {"origins": "http://localhost:3000"}},
    supports_credentials=True
)

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


# DB 초기화
init_db()


@app.route('/')
def home():
    return jsonify({"message": "AI Organizer API is running"}), 200


# ============================================
# 🔥 ChatGPT 정리 코칭 생성 함수 (최신 API 호환)
# ============================================
def generate_ai_advice(detections, score):
    """ YOLO 감지 결과 기반으로 ChatGPT 정리 코칭 생성 """

    try:
        detected_items = ", ".join([d["name"] for d in detections]) or "아무것도 감지되지 않음"

        prompt = f"""
너는 최고 수준의 방 정리 전문가야.

아래는 YOLO가 감지한 방의 물건 리스트야:
[{detected_items}]

이 방의 정리 점수는 {score}점이야.

이 정보를 기반으로 다음을 5~8줄로 간결하게 한국어로 작성해줘.
1) 방 전체 상태 요약
2) 정리 우선순위 TOP 3
3) 물건들을 어디에 정리하면 좋은지 (책상, 서랍, 옷장 등)
4) 전체적인 정리 루틴 제안
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 방 정리 전문가다."},
                {"role": "user", "content": prompt}
            ]
        )

        advice = response.choices[0].message.content
        return advice

    except Exception as e:
        print("ChatGPT 오류:", e)
        return "정리 조언 생성에 실패했습니다."


# ============================================
# 🎯 메인 이미지 분석 API
# ============================================
@app.route('/analyze', methods=['POST'])
def analyze_image():

    # 파일 체크
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # 1) YOLO 모델 추론
    try:
        detections, result_img_path = run_inference(filepath, RESULT_FOLDER)
    except Exception as e:
        return jsonify({'error': f'Model inference failed: {str(e)}'}), 500

    # 2) 점수 및 문제 분석
    try:
        report = analyze_results(detections)
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

    # 3) 히트맵 생성
    heatmap_path = None
    if detections:
        try:
            heatmap_filename = 'heatmap_' + file.filename
            heatmap_full_path = os.path.join(RESULT_FOLDER, heatmap_filename)
            generate_heatmap(filepath, detections, heatmap_full_path)
            heatmap_path = f"/results/{heatmap_filename}"
        except Exception as e:
            print("히트맵 생성 실패:", e)

    # 4) 🔥 ChatGPT 정리 조언 생성
    ai_advice = generate_ai_advice(detections, report["score"])

    # 5) DB 저장
    try:
        save_analysis(
            score=report['score'],
            detections=detections,
            report=report,
            image_name=file.filename
        )
    except Exception as e:
        print("DB 저장 실패:", e)

    # 6) 최종 응답 데이터 구성
    response_data = {
        "status": "success",
        "detections": detections,
        "report": report,
        "ai_advice": ai_advice,
        "result_image": f"/results/{os.path.basename(result_img_path)}"
    }

    if heatmap_path:
        response_data["heatmap_image"] = heatmap_path

    return jsonify(response_data)


# ============================================
# 📌 분석 기록/API
# ============================================
@app.route('/history', methods=['GET'])
def get_analysis_history():
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
    try:
        stats = get_statistics()
        return jsonify({
            "status": "success",
            "statistics": stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# 📌 결과 이미지 서빙
# ============================================
@app.route('/results/<path:filename>')
def serve_result_image(filename):
    return send_from_directory(RESULT_FOLDER, filename)


# ============================================
# 서버 실행
# ============================================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
