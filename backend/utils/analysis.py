# backend/utils/analysis.py
# 현실적인 방 정리정돈 분석 버전
# - 실제로 흔한 상황만 포함
# - 적절한 점수 밸런싱 (평균 70~80점대)

import math

# ==========================================
# 1. 현실적인 가중치 설정
# ==========================================

# 📌 물건별 기본 중요도 (현실적으로 조정)
OBJECT_WEIGHTS = {
    # 👕 옷 관련 (가장 흔함!) - 중요도 높음
    'shirt': 2.5,
    'pants': 2.5,
    'jacket': 2.5,
    'clothes': 2.5,
    'tie': 1.5,
    'shoe': 2.0,           # 신발
    'sneaker': 2.0,
    'socks': 1.8,
    
    # 🎒 가방류 (매우 흔함!)
    'backpack': 2.8,
    'handbag': 2.5,
    'suitcase': 3.0,       # 큰 짐
    
    # 📚 학습/업무 용품 (흔함)
    'book': 2.0,
    'notebook': 1.8,
    'laptop': 2.3,
    'keyboard': 1.5,
    'mouse': 1.3,
    'cell phone': 1.5,
    'remote': 1.2,
    
    # ☕ 음료 용기 (흔함)
    'cup': 2.2,
    'bottle': 2.0,
    'thermos': 2.0,
    
    # 🏀 운동/취미 용품
    'sports ball': 1.8,
    'baseball bat': 2.0,
    'tennis racket': 2.0,
    'skateboard': 2.2,
    'umbrella': 1.8,
    
    # 🧸 기타
    'teddy bear': 1.5,
    'pillow': 1.3,
    'blanket': 1.8,
    
    # 🪑 가구 (주변 정리 필요)
    'chair': 1.0,
    'bed': 0.8,
    'couch': 0.8,
}

# 📍 위치별 배수 (현실적으로 낮춤)
LOCATION_MULTIPLIERS = {
    'floor': 2.5,           # 바닥 (기존 4.0 → 2.5)
    'bed_surface': 2.0,     # 침대 위 (기존 3.0 → 2.0)
    'chair_surface': 1.8,   # 의자 위
    'desk': 1.5,            # 책상
    'table': 1.5,           # 테이블
    'shelf': 0.8,           # 선반 (정리됨)
    'normal': 1.2,          # 일반 위치
}


# ==========================================
# 2. 메인 분석 함수
# ==========================================

def analyze_results(detections):
    """
    실제 방 정리정돈 상황 기반 AI 분석
    - 흔한 상황 위주
    - 적절한 점수 밸런싱
    """
    
    if not detections:
        return {
            "score": 100, 
            "issues": [], 
            "suggestions": ["✨ 완벽하게 정리되어 있습니다!"]
        }
    
    total_penalty = 0
    issues = []
    suggestions = []
    
    # 이미지 크기
    max_y = max(obj['bbox'][3] for obj in detections)
    max_x = max(obj['bbox'][2] for obj in detections)
    
    # 카테고리별 카운트
    clothes_count = 0
    floor_items_count = 0
    bed_items_count = 0
    chair_items_count = 0
    desk_items_count = 0
    cup_count = 0
    
    # 🔍 각 물건 분석
    for obj in detections:
        name = obj['name'].lower()
        bbox = obj['bbox']
        
        # 기본 가중치
        base_weight = OBJECT_WEIGHTS.get(name, 1.5)
        
        # 위치 판단
        location = detect_location(bbox, max_x, max_y, detections)
        location_mult = LOCATION_MULTIPLIERS.get(location, 1.2)
        
        # 감점 계산 (기존보다 완화)
        penalty = base_weight * location_mult * 3  # 기존 *5 → *3
        total_penalty += penalty
        
        # 카테고리별 집계
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
                if desk_items_count <= 2:  # 책상은 좀 널널하게
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
            if location == 'floor' and bbox[3] > max_y * 0.7:  # 바닥 중앙
                suggestions.append(f"👟 {name}을 현관이나 신발장에 정리하세요")
                issues.append('shoe_floor')
        
        elif any(x in name for x in ['laptop', 'keyboard', 'mouse']):
            if location == 'floor':
                floor_items_count += 1
                suggestions.append(f"💻 바닥의 {name}을 책상으로 옮기세요")
                issues.append('electronics_floor')
        
        elif 'chair' in name:
            # 의자 주변 정리 (감점 적게)
            if chair_items_count > 2:
                suggestions.append(f"🪑 의자 주변을 정리하세요")
                issues.append('chair_cluttered')
    
    # 🔥 추가 상황별 페널티 (완화됨)
    
    # 1. 옷 개수 체크
    if clothes_count >= 5:
        total_penalty += 12  # 기존 15 → 12
        suggestions.append("👕 옷이 많이 흩어져 있습니다. 한꺼번에 정리하세요")
    elif clothes_count >= 3:
        total_penalty += 6   # 기존 10 → 6
    
    # 2. 바닥 어질러짐 심각도
    if floor_items_count >= 4:
        total_penalty += 10  # 기존 15 → 10
        suggestions.append("⚠️ 바닥에 물건이 많습니다. 우선 정리하세요")
    elif floor_items_count >= 2:
        total_penalty += 5   # 기존 8 → 5
    
    # 3. 침대 정리
    if bed_items_count >= 3:
        total_penalty += 8   # 기존 12 → 8
        suggestions.append("🛏️ 침대 위를 깨끗하게 정리하세요")
    
    # 4. 음료 용기
    if cup_count >= 3:
        total_penalty += 6   # 기존 10 → 6
        suggestions.append("☕ 컵/물병이 여러 개 있습니다. 싱크대로 옮기세요")
    
    # 5. 밀집도 (완화)
    clustering_penalty = calculate_clustering_penalty(detections)
    total_penalty += clustering_penalty
    
    if clustering_penalty > 8:  # 기존 10 → 8
        suggestions.append("💡 물건이 한곳에 몰려 있습니다. 분산 배치하세요")
    
    # 최종 점수 (0~100)
    score = max(0, min(100, 100 - int(total_penalty)))
    
    # 📋 종합 평가
    overall = generate_overall_feedback(score, clothes_count, floor_items_count)
    suggestions.insert(0, overall)
    
    # 중복 제거 및 제한 (최대 7개)
    unique_suggestions = list(dict.fromkeys(suggestions))[:7]
    
    return {
        "score": score,
        "issues": list(set(issues)),
        "suggestions": unique_suggestions
    }


# ==========================================
# 3. 위치 감지 (간소화)
# ==========================================

def detect_location(bbox, max_x, max_y, all_detections):
    """
    물건의 위치 판단 (현실적으로 간소화)
    """
    x1, y1, x2, y2 = bbox
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    
    # 바닥 판단 (하단 25%)
    if y2 > max_y * 0.75:
        return 'floor'
    
    # 침대 위 판단
    for obj in all_detections:
        if 'bed' in obj['name'].lower():
            bed_bbox = obj['bbox']
            if is_above(bbox, bed_bbox, threshold=30):
                return 'bed_surface'
    
    # 의자 위 판단
    for obj in all_detections:
        if 'chair' in obj['name'].lower():
            chair_bbox = obj['bbox']
            if is_above(bbox, chair_bbox, threshold=30):
                return 'chair_surface'
    
    # 책상/테이블 위 판단
    for obj in all_detections:
        obj_name = obj['name'].lower()
        if 'dining table' in obj_name or 'desk' in obj_name:
            table_bbox = obj['bbox']
            if is_above(bbox, table_bbox, threshold=40):
                return 'desk' if 'desk' in obj_name else 'table'
    
    # 선반
    for obj in all_detections:
        if 'shelf' in obj['name'].lower() or 'cabinet' in obj['name'].lower():
            return 'shelf'
    
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
# 4. 밀집도 분석 (완화)
# ==========================================

def calculate_clustering_penalty(detections):
    """
    밀집도 계산 (완화된 기준)
    """
    if len(detections) < 3:  # 2개 이하는 밀집 아님
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
    
    # 완화된 기준
    if avg_distance < 80:    # 기존 100
        return 12              # 기존 20
    elif avg_distance < 150:  # 기존 200
        return 6               # 기존 10
    else:
        return 0


# ==========================================
# 5. 종합 평가 생성
# ==========================================

def generate_overall_feedback(score, clothes_count, floor_items_count):
    """
    점수별 종합 피드백
    """
    # 특별 상황 체크
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


# ==========================================
# 6. 우선순위 계산 (선택 기능)
# ==========================================

def calculate_priority_scores(detections):
    """
    각 물건의 정리 우선순위 점수
    """
    if not detections:
        return []
    
    priorities = []
    max_y = max(obj['bbox'][3] for obj in detections)
    max_x = max(obj['bbox'][2] for obj in detections)
    
    for obj in detections:
        name = obj['name'].lower()
        bbox = obj['bbox']
        
        base_weight = OBJECT_WEIGHTS.get(name, 1.5)
        location = detect_location(bbox, max_x, max_y, detections)
        location_mult = LOCATION_MULTIPLIERS.get(location, 1.2)
        
        # 우선순위 점수 (0-100)
        priority = min(100, int(base_weight * location_mult * 12))
        
        priorities.append({
            'object': name,
            'bbox': bbox,
            'priority': priority,
            'location': location,
            'reasons': [
                f"위치: {location}",
                f"중요도: {base_weight}"
            ]
        })
    
    priorities.sort(key=lambda x: x['priority'], reverse=True)
    return priorities