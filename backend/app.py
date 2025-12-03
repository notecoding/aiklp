# backend/app.py
"""
완전 개선된 Flask 백엔드
- 3가지 AI 개선사항 모두 통합
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from model.infer import run_inference
from utils.analysis import analyze_results
from utils.heatmap import generate_heatmap
from utils.room_segmentation import visualize_room_zones, calculate_area_coverage
from utils.stacking_visualizer import visualize_stacks
from utils.object_tracker import get_tracker
from db import init_db, save_analysis, get_history, get_statistics
import os
from dotenv import load_dotenv
from openai import OpenAI

# ============================================
# 환경 변수 및 초기 설정
# ============================================
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️ WARNING: OPENAI_API_KEY 환경변수가 설정되지 않았습니다!")

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
    return jsonify({"message": "AI Organizer API is running - Full Enhanced Version"}), 200


# ============================================
# ChatGPT 조언 생성 (기존)
# ============================================
def generate_ai_advice(detections, score):
    """YOLO 감지 결과 기반으로 ChatGPT 정리 코칭 생성"""
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
# 🔥 메인 분석 API (완전 개선)
# ============================================
@app.route('/analyze', methods=['POST'])
def analyze_image():
    
    # 파일 체크
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # 1️⃣ 완전 개선된 추론 (Segmentation + 쌓임 탐지 포함)
    try:
        detections, result_img_path, room_masks, stacks = run_inference(filepath, RESULT_FOLDER)
        print(f"✅ 추론 완료: {len(detections)}개 객체, {len(stacks)}개 쌓임")
    except Exception as e:
        return jsonify({'error': f'Model inference failed: {str(e)}'}), 500

    # 2️⃣ 분석 (쌓임 정보 포함)
    try:
        report = analyze_results(detections)
        print(f"✅ 분석 완료: 점수 {report['score']}점")
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

    # 3️⃣ 히트맵 생성 (기존)
    heatmap_path = None
    if detections:
        try:
            heatmap_filename = 'heatmap_' + file.filename
            heatmap_full_path = os.path.join(RESULT_FOLDER, heatmap_filename)
            generate_heatmap(filepath, detections, heatmap_full_path)
            heatmap_path = f"/results/{heatmap_filename}"
            print("✅ 히트맵 생성 완료")
        except Exception as e:
            print(f"⚠️ 히트맵 생성 실패: {e}")

    # 4️⃣ 구역 시각화 생성 (Segmentation)
    zone_visualization_path = None
    area_coverage = None
    
    if room_masks is not None:
        try:
            zone_filename = 'zones_' + file.filename
            zone_full_path = os.path.join(RESULT_FOLDER, zone_filename)
            visualize_room_zones(filepath, room_masks, zone_full_path)
            zone_visualization_path = f"/results/{zone_filename}"
            
            area_coverage = calculate_area_coverage(room_masks)
            print("✅ 구역 시각화 생성 완료")
        except Exception as e:
            print(f"⚠️ 구역 시각화 실패: {e}")

    # 5️⃣ 쌓임 시각화 생성
    stacking_image_path = None
    
    if stacks:
        try:
            stacking_filename = 'stacks_' + file.filename
            stacking_full_path = os.path.join(RESULT_FOLDER, stacking_filename)
            visualize_stacks(filepath, detections, stacks, stacking_full_path)
            stacking_image_path = f"/results/{stacking_filename}"
            print(f"✅ 쌓임 시각화 생성: {len(stacks)}개 그룹")
        except Exception as e:
            print(f"⚠️ 쌓임 시각화 실패: {e}")

    # 6️⃣ 객체 추적 업데이트
    tracker = get_tracker()
    tracker.update(detections, file.filename)
    
    problem_objects = tracker.get_problem_objects(min_appearances=2)
    tracking_stats = tracker.get_statistics()
    
    print(f"✅ 추적 완료: {len(problem_objects)}개 반복 문제")

    # 7️⃣ ChatGPT 조언 생성 (추적 + 쌓임 정보 반영)
    ai_advice = generate_ai_advice(detections, report["score"])
    
    # 추적 정보 추가
    if problem_objects:
        chronic_warning = "\n\n🔄 반복되는 문제:\n"
        for prob in problem_objects[:3]:
            chronic_warning += f"- {prob['message']}\n"
        ai_advice += chronic_warning
    
    # 쌓임 정보 추가
    if stacks:
        stacking_warning = "\n\n⚠️ 쌓임 주의:\n"
        for stack in stacks[:3]:
            stacking_warning += f"- {stack['message']}\n"
        ai_advice += stacking_warning

    # 8️⃣ DB 저장
    try:
        save_analysis(
            score=report['score'],
            detections=detections,
            report=report,
            image_name=file.filename
        )
        print("✅ DB 저장 완료")
    except Exception as e:
        print(f"⚠️ DB 저장 실패: {e}")

    # 9️⃣ 최종 응답 데이터 구성
    response_data = {
        "status": "success",
        "detections": detections,
        "report": report,
        "ai_advice": ai_advice,
        "result_image": f"/results/{os.path.basename(result_img_path)}",
        
        # 🔥 Segmentation 데이터
        "segmentation": {
            "zone_image": zone_visualization_path,
            "area_coverage": area_coverage,
            "detected_areas": room_masks['detected_areas'] if room_masks else []
        },
        
        # 🔥 쌓임 데이터
        "stacking": {
            "stacks": stacks,
            "stacking_image": stacking_image_path,
            "total_stacks": len(stacks),
            "warning": (
                f"⚠️ {len(stacks)}개 그룹의 물건이 쌓여있거나 포개져있습니다!"
                if stacks else None
            )
        },
        
        # 🔥 추적 데이터
        "tracking": {
            "chronic_problems": problem_objects,
            "statistics": tracking_stats,
            "warning": (
                f"🔄 {len(problem_objects)}개 물건이 반복적으로 문제를 일으키고 있어요!"
                if problem_objects else None
            )
        }
    }

    if heatmap_path:
        response_data["heatmap_image"] = heatmap_path

    print("✅ 모든 분석 완료!")
    return jsonify(response_data)


# ============================================
# 기존 API 엔드포인트들
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


@app.route('/tracking/reset', methods=['POST'])
def reset_tracking():
    """추적 정보 초기화"""
    try:
        tracker = get_tracker()
        tracker.reset()
        return jsonify({
            "status": "success",
            "message": "추적 정보가 초기화되었습니다."
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/tracking/stats', methods=['GET'])
def get_tracking_stats():
    """추적 통계 조회"""
    try:
        tracker = get_tracker()
        stats = tracker.get_statistics()
        problems = tracker.get_problem_objects()
        
        return jsonify({
            "status": "success",
            "statistics": stats,
            "chronic_problems": problems
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/results/<path:filename>')
def serve_result_image(filename):
    return send_from_directory(RESULT_FOLDER, filename)


# ============================================
# 서버 실행
# ============================================
if __name__ == "__main__":
    print("="*50)
    print("🚀 AI 정리 정돈 도우미 - 완전 개선 버전")
    print("="*50)
    print("✅ Segmentation 기반 구역 분석")
    print("✅ 객체 추적 (반복 문제 탐지)")
    print("✅ 쌓임/포개짐 자동 감지")
    print("="*50)
    app.run(debug=True, host="0.0.0.0", port=5000)
