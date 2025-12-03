# backend/utils/analysis.py
"""
완전 개선된 분석 모듈
- 기존 룰 기반 분석
- Segmentation 정보 활용
- 쌓임 패턴 반영
"""

import math
from utils.stacking_detector import get_stacking_detector

# ==========================================
# 1. 현실적인 가중치 설정 (기존 유지)
# ==========================================

OBJECT_WEIGHTS = {
    'shirt': 2.5, 'pants': 2.5, 'jacket': 2.5, 'clothes': 2.5,
    'tie': 1.5, 'shoe': 2.0, 'sneaker': 2.0, 'socks': 1.8,
    'backpack': 2.8, 'handbag': 2.5, 'suitcase': 3.0,
    'book': 2.0, 'notebook': 1.8, 'laptop': 2.3,
    'keyboard': 1.5, 'mouse': 1.3, 'cell phone': 1.5, 'remote': 1.2,
    'cup': 2.2, 'bottle': 2.0, 'thermos': 2.0,
    'sports ball': 1.8, 'baseball bat': 2.0, 'tennis racket': 2.0,
    'skateboard': 2.2, 'umbrella': 1.8,
    'teddy bear': 1.5, 'pillow': 1.3, 'blanket': 1.8,
    'chair': 1.0, 'bed': 0.8, 'couch': 0.8,
}

LOCATION_MULTIPLIERS = {
    'floor': 2.5,
    'bed_surface': 2.0,
    'chair_surface': 1.8,
    'desk': 1.5,
    'table': 1.5,
    'shelf': 0.8,
    'wall_shelf': 0.8,
    'furniture': 1.0,
    'normal': 1.2,
}


# ==========================================
# 2. 메인 분석 함수 (완전 개선)
# ==========================================

def analyze_results(detections):
    """
    완전 개선된 방 정리정돈 분석
    - 기존 룰 기반 분석
    - Segmentation 기반 정확한 위치
    - 쌓임 패턴 탐지
    """
    
    if not detections:
        return {
            "score": 100, 
            "issues": [], 
            "suggestions": ["✨ 완벽하게 정리되어 있습니다!"],
            "stacks": []
        }
    
    total_penalty = 0
    issues = []
    suggestions = []
    
    # 🔥 쌓임 탐지
    print("📊 쌓임 패턴 분석 중...")
    stacking_detector = get_stacking_detector()
    stacks = stacking_detector.detect_stacks(detections)
    stacking_penalty = stacking_detector.calculate_stacking_score(stacks)
    
    total_penalty += stacking_penalty
    
    # 쌓임 관련 이슈 및 제안
    if stacks:
        print(f"⚠️ {len(stacks)}개 쌓임 그룹 발견")
        for stack in stacks:
            issues.append(f"{stack['type']}_{stack['object']}")
            
            if stack['type'] == 'vertical_stack':
                suggestions.insert(0, 
                    f"⚠️ {stack['object']} {stack['count']}개가 수직으로 쌓여있습니다! "
                    f"넘어질 위험이 있으니 수평으로 펼쳐 정리하세요."
                )
            elif stack['type'] == 'overlapping_pile':
                suggestions.insert(0,
                    f"📚 {stack['object']} {stack['count']}개가 포개져있습니다. "
                    f"펼쳐서 정리하면 필요한 것을 쉽게 찾을 수 있어요."
                )
    
    # 이미지 크기 (폴백)
    max_y = max(obj['bbox'][3] for obj in detections)
    max_x = max(obj['bbox'][2] for obj in detections)
    
    # 카테고리별 카운트
    clothes_count = 0
    floor_items_count = 0
    bed_items_count = 0
    chair_items_count = 0
    desk_items_count = 0
    cup_count = 0
    
    # 🔍 각 물건 분석 (Segmentation 정보 활용)
    for obj in detections:
        name = obj['name'].lower()
        bbox = obj['bbox']
        
        # 기본 가중치
        base_weight = OBJECT_WEIGHTS.get(name, 1.5)
        
        # 🔥 Segmentation 기반 위치 (있으면 사용)
        location = obj.get('location', 'unknown')
        
        # 위치를 못 찾았으면 폴백
        if location == 'unknown':
            location = detect_location_fallback(bbox, max_x, max_y, detections)
        
        location_mult = LOCATION_MULTIPLIERS.get(location, 1.2)
        
        # 감점 계산
        penalty = base_weight * location_mult * 3
        total_penalty += penalty
        
        # 카테고리별 집계 및 제안
        if any(x in name for x in ['shirt', 'pants', 'jacket', 'clothes', 'tie', 'shoe', 'socks']):
            clothes_count += 1
            if location == 'floor':
                floor_items_count += 1
                suggestions.append(f"👕 바닥의 {name}을 세탁기나 옷장에 정리하세요")
                issues.append('clothes_floor')
            elif location == 'bed_surface':
                bed_items_count += 1
                suggestions.append(f"🛏️ 침대 위의 {name}을 옷장에 걸어두세요")
                issues.append('clothes_bed')
            elif location == 'chair_surface':
                chair_items_count += 1
                suggestions.append(f"🪑 의자 위의 {name}을 옷장에 정리하세요")
                issues.append('clothes_chair')
        
        elif any(x in name for x in ['backpack', 'handbag', 'suitcase']):
            if location == 'floor':
                floor_items_count += 1
                suggestions.append(f"🎒 바닥의 {name}을 수납공간에 정리하세요")
                issues.append('bag_floor')
            elif location == 'bed_surface':
                bed_items_count += 1
                suggestions.append(f"🛏️ 침대 위의 {name}을 내려놓으세요")
                issues.append('bag_bed')
        
        elif 'book' in name:
            if location == 'floor':
                floor_items_count += 1
                suggestions.append(f"📚 바닥의 {name}을 책장이나 책상에 정리하세요")
                issues.append('book_floor')
            elif location == 'desk':
                desk_items_count += 1
                if desk_items_count <= 2:
                    suggestions.append(f"📖 책상의 {name}을 서랍에 정리하세요")
                issues.append('book_desk')
        
        elif any(x in name for x in ['cup', 'bottle', 'thermos']):
            cup_count += 1
            if location in ['floor', 'bed_surface']:
                suggestions.append(f"☕ {location}의 {name}을 싱크대로 옮기세요")
                issues.append('cup_misplaced')
            elif cup_count > 1:
                suggestions.append(f"☕ {name}을 싱크대로 옮기세요")
        
        elif any(x in name for x in ['sports ball', 'baseball bat', 'skateboard', 'tennis racket']):
            if location == 'floor':
                floor_items_count += 1
                suggestions.append(f"🏀 바닥의 {name}을 수납공간에 정리하세요")
                issues.append('sports_floor')
        
        elif 'shoe' in name or 'sneaker' in name:
            if location == 'floor' and bbox[3] > max_y * 0.7:
                suggestions.append(f"👟 {name}을 현관이나 신발장에 정리하세요")
                issues.append('shoe_floor')
        
        elif any(x in name for x in ['laptop', 'keyboard', 'mouse']):
            if location == 'floor':
                floor_items_count += 1
                suggestions.append(f"💻 바닥의 {name}을 책상으로 옮기세요")
                issues.append('electronics_floor')
        
        elif 'chair' in name:
            if chair_items_count > 2:
                suggestions.append(f"🪑 의자 주변을 정리하세요")
                issues.append('chair_cluttered')
    
    # 🔥 추가 상황별 페널티
    
    # 1. 옷 개수
    if clothes_count >= 5:
        total_penalty += 12
        suggestions.append("👕 옷이 많이 흩어져 있습니다. 한꺼번에 정리하세요")
    elif clothes_count >= 3:
        total_penalty += 6
    
    # 2. 바닥 어질러짐
    if floor_items_count >= 4:
        total_penalty += 10
        suggestions.append("⚠️ 바닥에 물건이 많습니다. 우선 정리하세요")
    elif floor_items_count >= 2:
        total_penalty += 5
    
    # 3. 침대 정리
    if bed_items_count >= 3:
        total_penalty += 8
        suggestions.append("🛏️ 침대 위를 깨끗하게 정리하세요")
    
    # 4. 음료 용기
    if cup_count >= 3:
        total_penalty += 6
        suggestions.append("☕ 컵/물병이 여러 개 있습니다. 싱크대로 옮기세요")
    
    # 5. 밀집도
    clustering_penalty = calculate_clustering_penalty(detections)
    total_penalty += clustering_penalty
    
    if clustering_penalty > 8:
        suggestions.append("💡 물건이 한곳에 몰려 있습니다. 분산 배치하세요")
    
    # 최종 점수 (0~100)
    score = max(0, min(100, 100 - int(total_penalty)))
    
    # 📋 종합 평가
    overall = generate_overall_feedback(score, clothes_count, floor_items_count, stacks)
    suggestions.insert(0, overall)
    
    # 중복 제거 및 제한 (최대 10개)
    unique_suggestions = list(dict.fromkeys(suggestions))[:10]
    
    return {
        "score": score,
        "issues": list(set(issues)),
        "suggestions": unique_suggestions,
        "stacks": stacks  # 🔥 쌓임 정보 포함
    }


# ==========================================
# 3. 위치 감지 폴백 (Segmentation 실패 시)
# ==========================================

def detect_location_fallback(bbox, max_x, max_y, all_detections):
    """Segmentation 없을 때 폴백 위치 판단"""
    x1, y1, x2, y2 = bbox
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    
    # 바닥 판단
    if y2 > max_y * 0.75:
        return 'floor'
    
    # 침대 위
    for obj in all_detections:
        if 'bed' in obj['name'].lower():
            bed_bbox = obj['bbox']
            if is_above(bbox, bed_bbox, threshold=30):
                return 'bed_surface'
    
    # 의자 위
    for obj in all_detections:
        if 'chair' in obj['name'].lower():
            chair_bbox = obj['bbox']
            if is_above(bbox, chair_bbox, threshold=30):
                return 'chair_surface'
    
    # 책상/테이블
    for obj in all_detections:
        obj_name = obj['name'].lower()
        if 'dining table' in obj_name or 'desk' in obj_name:
            table_bbox = obj['bbox']
            if is_above(bbox, table_bbox, threshold=40):
                return 'desk' if 'desk' in obj_name else 'table'
    
    return 'normal'


def is_above(bbox1, bbox2, threshold=30):
    """bbox1이 bbox2 위에 있는지"""
    _, y1 = center(bbox1)
    _, y2 = center(bbox2)
    return (y1 + threshold) < y2


def center(bbox):
    """중심 좌표"""
    x1, y1, x2, y2 = bbox
    return (x1 + x2) / 2, (y1 + y2) / 2


# ==========================================
# 4. 밀집도 분석
# ==========================================

def calculate_clustering_penalty(detections):
    """밀집도 계산"""
    if len(detections) < 3:
        return 0
    
    centers = [center(obj['bbox']) for obj in detections]
    
    total_distance = 0
    count = 0
    
    for i in range(len(centers)):
        for j in range(i+1, len(centers)):
            dist = math.sqrt(
                (centers[i][0] - centers[j][0])**2 + 
                (centers[i][1] - centers[j][1])**2
            )
            total_distance += dist
            count += 1
    
    avg_distance = total_distance / count if count > 0 else 0
    
    if avg_distance < 80:
        return 12
    elif avg_distance < 150:
        return 6
    else:
        return 0


# ==========================================
# 5. 종합 평가 생성 (쌓임 정보 반영)
# ==========================================

def generate_overall_feedback(score, clothes_count, floor_items_count, stacks):
    """점수별 종합 피드백 (쌓임 고려)"""
    
    # 🔥 쌓임 심각도 체크
    high_severity_stacks = [s for s in stacks if s['severity'] == 'high']
    
    if high_severity_stacks:
        return f"🚨 위험! {len(high_severity_stacks)}개 그룹이 쌓여 넘어질 수 있습니다. 즉시 정리하세요!"
    
    # 특별 상황
    if clothes_count >= 5 and floor_items_count >= 3:
        return "⚠️ 옷과 물건이 많이 흩어져 있습니다. 전체적인 정리가 필요해요"
    
    if floor_items_count >= 4:
        return "📦 바닥에 물건이 많습니다. 바닥부터 정리 시작하세요"
    
    # 점수별 기본 피드백
    if score >= 90:
        return "✨ 완벽합니다! 이 상태를 유지하세요"
    elif score >= 80:
        return "😊 매우 깔끔합니다! 조금만 더 신경쓰면 완벽해요"
    elif score >= 70:
        return "👍 깔끔한 편입니다. 아래 제안 참고하세요"
    elif score >= 60:
        return "📝 정리가 필요합니다. 차근차근 정리해보세요"
    elif score >= 50:
        return "🧹 상당한 정리가 필요합니다. 우선순위부터 시작하세요"
    else:
        return "🚨 전체적인 정리가 시급합니다!"
