# backend/model/infer.py
"""
완전 개선된 추론 모듈
- YOLO 객체 탐지
- Segmentation 기반 정확한 위치 판단
- 쌓임 패턴 탐지
"""
from ultralytics import YOLO
import cv2
import os
import sys

# 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.room_segmentation import segment_room_areas, detect_object_location_precise
from utils.stacking_detector import get_stacking_detector

# YOLO 모델 로드
model = YOLO("yolov8x.pt")

def run_inference(image_path, result_dir):
    """
    완전 개선된 이미지 분석
    1. 객체 탐지 (YOLO)
    2. 구역 분할 (Segmentation)
    3. 정확한 위치 판단
    4. 쌓임 패턴 탐지
    
    Returns:
        tuple: (detections, result_path, room_masks, stacks)
    """
    
    # 1️⃣ 기존 객체 탐지
    print("🔍 Step 1: 객체 탐지 중...")
    results = model.predict(source=image_path, conf=0.4, verbose=False)
    
    detections = []
    img = cv2.imread(image_path)
    
    for box in results[0].boxes:
        cls = int(box.cls[0])
        name = model.names[cls]
        conf = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        
        detections.append({
            "name": name,
            "conf": round(conf, 2),
            "bbox": [x1, y1, x2, y2]
        })
    
    print(f"✅ {len(detections)}개 객체 탐지 완료")
    
    # 2️⃣ Segmentation 기반 구역 분할
    print("🔍 Step 2: 구역 분할 중...")
    room_masks = None
    try:
        room_masks = segment_room_areas(image_path)
        print(f"✅ {len(room_masks['detected_areas'])}개 구역 분할 완료")
        
        # 3️⃣ 각 객체의 정확한 위치 판단
        print("🔍 Step 3: 위치 판단 중...")
        for detection in detections:
            precise_location = detect_object_location_precise(
                detection['bbox'], 
                room_masks
            )
            detection['location'] = precise_location
            detection['location_method'] = 'segmentation'
        
        print("✅ 위치 판단 완료")
        
    except Exception as e:
        print(f"⚠️ Segmentation 실패, 기본 방식 사용: {e}")
        
        # 폴백: 기본 위치 판단
        for detection in detections:
            detection['location'] = _fallback_location(detection['bbox'], img.shape)
            detection['location_method'] = 'fallback'
    
    # 4️⃣ 쌓임 패턴 탐지
    print("🔍 Step 4: 쌓임 패턴 탐지 중...")
    stacks = []
    try:
        stacking_detector = get_stacking_detector()
        stacks = stacking_detector.detect_stacks(detections)
        print(f"✅ {len(stacks)}개 쌓임 그룹 탐지 완료")
    except Exception as e:
        print(f"⚠️ 쌓임 탐지 실패: {e}")
    
    # 5️⃣ 시각화
    print("🎨 시각화 생성 중...")
    for detection in detections:
        x1, y1, x2, y2 = detection['bbox']
        location = detection.get('location', 'unknown')
        
        # 위치별 색상
        color_map = {
            'floor': (0, 0, 255),        # 빨강
            'bed_surface': (0, 255, 255), # 노랑
            'desk': (0, 255, 0),          # 초록
            'furniture': (255, 128, 0),   # 주황
            'wall_shelf': (255, 0, 255),  # 마젠타
            'normal': (128, 128, 128)     # 회색
        }
        color = color_map.get(location, (255, 255, 255))
        
        # 박스 그리기
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        
        # 라벨
        label = f"{detection['name']} ({detection['conf']:.2f})"
        label_with_loc = f"{label} [{location}]"
        
        # 배경
        (text_w, text_h), _ = cv2.getTextSize(
            label_with_loc, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
        )
        cv2.rectangle(img, (x1, y1 - text_h - 5), (x1 + text_w, y1), color, -1)
        
        # 텍스트
        cv2.putText(img, label_with_loc, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # 쌓임 그룹 표시
    for stack in stacks:
        x1, y1, x2, y2 = stack['bounding_box']
        stack_color = (0, 0, 255) if stack['severity'] == 'high' else (0, 165, 255)
        
        # 반투명 박스
        overlay = img.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), stack_color, -1)
        img = cv2.addWeighted(img, 0.7, overlay, 0.3, 0)
        
        # 테두리
        cv2.rectangle(img, (x1, y1), (x2, y2), stack_color, 3)
        
        # 라벨
        stack_label = f"STACK: {stack['object']} x{stack['count']}"
        cv2.putText(img, stack_label, (x1 + 5, y1 + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # 결과 이미지 저장
    result_path = os.path.join(result_dir, os.path.basename(image_path))
    cv2.imwrite(result_path, img)
    print(f"✅ 결과 저장: {result_path}")
    
    return detections, result_path, room_masks, stacks


def _fallback_location(bbox, img_shape):
    """Segmentation 실패 시 폴백 위치 판단"""
    h, w = img_shape[:2]
    x1, y1, x2, y2 = bbox
    
    if y2 > h * 0.75:
        return 'floor'
    elif y1 < h * 0.3:
        return 'wall_shelf'
    else:
        return 'normal'
